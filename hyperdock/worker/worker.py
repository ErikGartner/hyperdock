from threading import Thread
import logging
from time import sleep
import secrets
from datetime import datetime
import platform

from ..common.workqueue import WorkQueue
from ..common.experiment import Experiment

SLEEP_TIME = 10


class Worker(Thread):

    def __init__(self, mongodb, docker_env, parallelism=1, in_docker=False):
        super().__init__(name='Worker')

        self._mongodb = mongodb
        self.id = self._generate_id()
        self.logger = logging.getLogger('Worker %s' % self.id)
        self._running = True
        self.workqueue = WorkQueue(mongodb)
        self.experiments = []
        self.max_experiments = parallelism
        self.docker_env = docker_env
        self.in_docker = in_docker

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
        host_name = platform.node()
        host = '(Docker) %s' % host_name if self.in_docker else host_name

        data = {
            'id': self.id,
            'time': datetime.utcnow(),
            'parallelism': self.max_experiments,
            'jobs': [e.id for e in self.experiments],
            'env': self.docker_env,
            'host': host,
        }
        self._mongodb.workers.update_one({'id': self.id}, {'$set': data},
                                         upsert=True)

    def _monitor_experiments(self):
        """
        Monitor the status of the current experiments.
        Also checks to see if an experiment has been cancelled by the user.
        """
        running_exps = []
        for ex in self.experiments:
            if self.workqueue.is_job_cancelled(ex.id):
                # Experiment was cancelled by user
                ex.cleanup()
                continue

            if ex.is_running():
                # Update the stay alive
                self._update_experiment(ex)
                running_exps.append(ex)
            else:
                # Wrap up the finished experiment
                self._cleanup_experiment(ex)
        self.experiments = running_exps

    def _update_experiment(self, experiment):
        """
        Takes and experiment and updates the workqueue.
        """
        self.workqueue.update_job(experiment.id, experiment.get_update())

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
            if job is None:
                break

            experiment = experiment_cls(job, self.docker_env)
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
