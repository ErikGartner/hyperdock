import logging

import docker


class Experiment:
    """
    Class managing an experiment.
    """

    def __init__(self, job):
        super().__init__()

        self._queue_job = job
        self.id = job['_id']
        self.logger = logging.getLogger('Experiment %s' % self.id)

    def start(self):
        """
        Starts the experiment.
        """
        image = self._queue_job['data']['docker']['image']
        container = self._start_container(image)
        if container is None:
            pass


    def stop(self):
        """
        Stops the experiment.
        """
        pass

    def cleanup(self):
        """
        Stops and removes temporary files.
        """
        pass

    def is_running(self):
        """
        Checks with underlying runner if the current experiment is running.
        Otherwise it could: not be started, finished or failed.
        """
        pass

    def get_result(self):
        """
        Returns the result, that is: state, loss, and any extra data.
        """
        pass

    def _start_container(self, image):
        """
        Starts a docker container and returns its handle.
        """

        try:
            container = self.docker_client.containers.run(
                image=image,
                tty=False,
                detach=True,
                environment=json.loads({}),
                runtime='',
                log_config={'type': 'json-file'},
                stdout=True,
                stderr=True,
                volumes=[])
            return container

        except (docker.errors.ContainerError, docker.errors.APIError,
                docker.errors.ImageNotFound) as e:
            self.logger.error(e)
            return None

    def __str__(self):
        return 'Experiment: %s' % self._queue_job


class MockExperiment(Experiment):
    """
    A mock experiment that doesn't actually run any experiment.
    It runs for one check then finishes. Returns a loss of 1.0.
    """

    def __init__(self, job):
        super().__init__(job)
        self.running = False
        self.failure = False

    def start(self):
        self.running = True
        self.failure = False

    def is_running(self):
        r = self.running
        self.running = False
        return r

    def stop(self):
        self.running = False
        self.failure = True

    def get_result(self):
        state = 'ok' if not self.failure else 'failure'
        return {'loss': 1.0, 'state': state}
