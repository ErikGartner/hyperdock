from threading import Thread
import logging
from time import sleep

from sklearn.model_selection import ParameterGrid

from ..common.trialqueue import TrialQueue
from ..common.workqueue import WorkQueue

SLEEP_TIME = 5


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
        experiments_specs = list(ParameterGrid(trial['param_space']))
        for payload in experiments_specs:
            self.workqueue.add_job(payload, trial['priority'])
