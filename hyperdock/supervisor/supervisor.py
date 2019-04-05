from threading import Thread
import logging
from time import sleep
from datetime import datetime, timedelta

from ..common.trialqueue import TrialQueue
from ..common.workqueue import WorkQueue, WORK_TIMEOUT
from .search import Grid

SLEEP_TIME = 15


class Supervisor(Thread):
    """
    The supervisor thread is the main thread that reads new
    trial specifications and creates experiments for the
    workers.
    """

    def __init__(self, mongodb, in_docker=False):
        super().__init__(name="Supervisor")

        self._logger = logging.getLogger("Supervisor")
        self._mongodb = mongodb
        self._trialqueue = TrialQueue(mongodb)
        self._workqueue = WorkQueue(mongodb)
        self._worker_collection = mongodb.workers
        self._in_docker = in_docker
        self._running = False
        self._sleep_time = SLEEP_TIME

    def run(self):
        """
        The main loop of the worker.
        It checks the trial queue for new specification.
        If it finds a trial it will process it by queuing new
        experiments.
        """
        self._logger.info("Started main loop")
        self._running = True

        while self._running:
            self._purge_old_workers()
            self._process_trials()
            self._trialqueue.update_trials()
            self._purge_dead_jobs()
            self._cancel_abandoned_jobs()
            sleep(self._sleep_time)

    def stop(self):
        """
        Request a stop of the supervisor.
        """
        self._running = False

    def _process_trials(self):
        """
        Dequeues the trial queue and create experiments.
        """
        trial = self._trialqueue.next_trial()
        while trial is not None:
            self._process_trial(trial)
            trial = self._trialqueue.next_trial()

    def _process_trial(self, trial):
        """
        Takes a trial experiment, expands the parameter space and
        adds experiments to the work queue.
        """
        params_list = Grid.expand(trial["param_space"])

        for params in params_list:
            self._workqueue.add_job(
                params,
                trial["data"],
                trial["_id"],
                trial["name"],
                trial["priority"],
            )

    def _purge_old_workers(self):
        """
        The supervisor checks the latests registered workers and cleans up
        timed out workers.
        """
        t = datetime.utcnow() - timedelta(seconds=WORK_TIMEOUT)
        self._worker_collection.remove({"time": {"$lt": t}})

    def _purge_dead_jobs(self):
        """
        Removes dead jobs and re-queues them if there are enough retries left.
        """
        dead_jobs = self._workqueue.purge_dead_jobs()
        for job in dead_jobs:
            retry = self._trialqueue.use_retry_ticket(job["trial"])
            if not retry:
                # No more retries
                return

            self._logger.info(
                "Retried timed out job %s for trial %s"
                % (job["_id"], job["trial"])
            )
            self._workqueue.add_job(
                job["parameters"], job["data"], job["trial"], job["priority"]
            )

    def _cancel_abandoned_jobs(self):
        """
        All jobs not associated with a live trial will be cancelled.
        """
        live_trials = self._trialqueue.get_live_trials()
        jobs = self._workqueue.cancel_invalid_jobs(live_trials)
        if len(jobs) > 0:
            self._logger.info("Cancelled: {}".format(jobs))
