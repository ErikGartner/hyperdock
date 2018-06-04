from threading import Thread
import logging
from time import sleep
from datetime import datetime, timedelta

from sklearn.model_selection import ParameterGrid

from ..common.trialqueue import TrialQueue
from ..common.workqueue import WorkQueue

SLEEP_TIME = 5
WORKER_TIMEOUT = 300


class Supervisor(Thread):
    """
    The supervisor thread is the main thread that reads new
    trial specifications and creates experiments for the
    workers.
    """

    def __init__(self, mongodb):
        super().__init__(name='Supervisor')

        self.logger = logging.getLogger('Supervisor')
        self._mongodb = mongodb
        self.trialqueue = TrialQueue(mongodb)
        self.workqueue = WorkQueue(mongodb)
        self.worker_collection = mongodb.workers
        self._running = True

    def run(self):
        """
        The main loop of the worker.
        It checks the trial queue for new specification.
        If it finds a trial it will process it by queuing new
        experiments.
        """
        self.logger.info('Started main loop')

        while self._running:
            self._purge_old_workers()
            self._process_trials()
            sleep(SLEEP_TIME)

    def stop(self):
        """
        Request a stop of the supervisor.
        """
        self._running = False

    def _process_trials(self):
        """
        Dequeues the trial queue and create experiments.
        """
        trial = self.trialqueue.next_trial()
        while trial is not None:
            self._process_trial(trial)
            trial = self.trialqueue.next_trial()

    def _process_trial(self, trial):
        """
        Takes a trial experiment, expands the parameter space and
        adds experiments to the work queue.
        """
        params_list = list(ParameterGrid(trial['param_space']))

        for params in params_list:
            self.workqueue.add_job(params, trial['data'], trial['priority'])

    def _purge_old_workers(self):
        """
        The supervisor checks the latests registered workers and cleans up
        timed out workers.
        """
        t = datetime.utcnow() - timedelta(seconds=WORKER_TIMEOUT)
        self.worker_collection.remove({'time': {'$lt': t}})
