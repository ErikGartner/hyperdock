from threading import Thread
import logging
from time import sleep
import secrets
from datetime import datetime


SLEEP_TIME = 5


class Worker(Thread):

    def __init__(self, args, mongodb):
        super().__init__(name="Worker")

        self._mongodb = mongodb
        self.id = self._generate_id()
        self.logger = logging.getLogger('Worker %s' % self.id)
        self._running = True

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
        pass

    def _start_new_experiments(self):
        """
        If not the max concurrent number of experiments is reached,
        starta new experiment.
        """
        pass

    def _shutdown(self):
        """
        Performs an immediate but graceful shutdown of the worker and
        experiments.
        """
        pass

    def _generate_id(self):
        """
        Generates a unique worker id
        """
        return 'worker-%s' % secrets.token_hex(16)
