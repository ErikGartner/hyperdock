from threading import Thread
import logging
from time import sleep
import secrets
from datetime import datetime

from ..common.workqueue import WorkQueue
from ..common.experiment import Experiment

SLEEP_TIME = 5


class Worker(Thread):

    def __init__(self, args, mongodb):
        super().__init__(name='Worker')

        self._mongodb = mongodb
        self.id = self._generate_id()
        self.logger = logging.getLogger('Worker %s' % self.id)
        self._running = True
        self.workqueue = WorkQueue(mongodb)
        self.experiments = []
        self.max_experiments = 1

    def run(self):
        """
        The main loop of the worker.
        It does the following:
            - Update keep alive
            - Check for experiments to finish
            - Check for new work
        """
        self.logger.info('Started main loop')

        while self._running:
            self._register_worker()
            self._monitor_experiments()
            self._start_new_experiments()
            sleep(SLEEP_TIME)

        self._shutdown()

    def stop(self):
        """
        Request a stop of the worker.
        """
        self._running = False

    def _register_worker(self):
        """
        Updates the worker list with this worker.
        Also used as a keep-alive message.
        """
        data = {
            'id': self.id,
            'time': datetime.utcnow(),
        }
        self._mongodb.workers.update_one({'id': self.id}, {'$set': data},
                                         upsert=True)

    def _monitor_experiments(self):
        """
        Monitor the status of the current experiments.
        """
        exps = []
        for ex in self.experiments:
            if ex.is_running():
                # Update the stay alive
                self.workqueue.update_job(ex.id)
                exps.append(ex)
            else:
                # Wrap up the finished experiment
                self._cleanup_experiment(ex)
        self.experiments = exps

    def _cleanup_experiment(self, experiment):
        """
        Takes an ended experiment and updates the work queue.
        """
        res = experiment.get_result()
        experiment.cleanup()
        self.workqueue.finish_job(experiment.id, res)

    def _start_new_experiments(self, experiment_cls=Experiment):
        """
        If not the max concurrent number of experiments is reached,
        starta new experiment.
        """
        for i in range(self.max_experiments - len(self.experiments)):
            job = self.workqueue.assign_next_job(self.id)
            experiment = experiment_cls(job)
            experiment.start()
            self.experiments.append(experiment)

    def _shutdown(self):
        """
        Performs an immediate but graceful shutdown of the worker and
        experiments.
        """
        for ex in self.experiments:
            ex.stop()
            res = ex.get_result()
            self.workqueue.finish_job(ex.id, res)
        self.experiments = []

    def _generate_id(self):
        """
        Generates a unique worker id.
        """
        return 'worker-%s' % secrets.token_hex(16)