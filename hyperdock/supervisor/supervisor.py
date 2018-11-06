from threading import Thread
import logging
from time import sleep
from datetime import datetime, timedelta

from sklearn.model_selection import ParameterGrid

from ..common.trialqueue import TrialQueue
from ..common.workqueue import WorkQueue, WORK_TIMEOUT

SLEEP_TIME = 15


class Supervisor(Thread):
    """
    The supervisor thread is the main thread that reads new
    trial specifications and creates experiments for the
    workers.
    """

    def __init__(self, mongodb, in_docker=False):
        super().__init__(name='Supervisor')

        self.logger = logging.getLogger('Supervisor')
        self._mongodb = mongodb
        self.trialqueue = TrialQueue(mongodb)
        self.workqueue = WorkQueue(mongodb)
        self.worker_collection = mongodb.workers
        self.in_docker = in_docker
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
            self.trialqueue.update_trials()
            self._purge_dead_jobs()
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
        params_list = self._expand_parameter_space(trial['param_space'])

        for params in params_list:
            self.workqueue.add_job(params, trial['data'], trial['_id'],
                                   trial['name'], trial['priority'])

    def _expand_parameter_space(self, param_spaces):
        """
        Takes a parameter space configuration and expands it to all combinations.
        Either a dictionary or a list of dictionaries.
        """
        if not isinstance(param_spaces, list):
            param_spaces = [param_spaces]

        params_list = []
        for param_space in param_spaces:
            fixed_params = {}
            variable_params = {}
            for k, v in param_space.items():
                if isinstance(v, list):
                    variable_params[k] = v
                else:
                    fixed_params[k] = v

            params = list(ParameterGrid(variable_params))
            for param_set in params:
                param_set.update(fixed_params)

            params_list.extend(params)

        return params_list

    def _purge_old_workers(self):
        """
        The supervisor checks the latests registered workers and cleans up
        timed out workers.
        """
        t = datetime.utcnow() - timedelta(seconds=WORK_TIMEOUT)
        self.worker_collection.remove({'time': {'$lt': t}})

    def _purge_dead_jobs(self):
        """
        Removes dead jobs and re-queues them if there are enough retries left.
        """
        dead_jobs = self.workqueue.purge_dead_jobs()
        for job in dead_jobs:
            if job is None:
                continue

            retry = self.trialqueue.use_retry_ticket(job['trial'])
            if not retry:
                # No more retries
                return

            self.logger.info('Retried timed out job %s for trial %s' %
                             (job['_id'], job['trial']))
            self.workqueue.add_job(job['parameters'],
                                   job['data'],
                                   job['trial'],
                                   job['priority'])
