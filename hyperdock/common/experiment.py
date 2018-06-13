import logging
from datetime import datetime
import os
import json

import docker

from .utils import try_key

LOG_TAIL_ROWS = 100


class Experiment:
    """
    Class managing an experiment.
    """

    def __init__(self, job, worker_env):
        super().__init__()

        self._queue_job = job
        self.id = job['_id']
        self.logger = logging.getLogger('Experiment %s' % self.id)
        self._is_running = False
        self._result = {}
        self._container = None
        self._volumes = []
        self._volume_root = None
        self._docker_client = docker.from_env()
        self.has_started = False
        self.worker_env = worker_env
        self._last_update = {}

    def start(self):
        """
        Start the experiment.
        """
        if self.has_started:
            raise RuntimeError('This experiment has already been executed.')
        self.has_started = True

        self._is_running = True
        self._setup_volumes()
        image = self._queue_job['data']['docker']['image']
        self._container = self._start_container(image)

        if self._container is None:
            self._is_running = False

    def stop(self):
        """
        Stops the experiment.
        """
        if self._is_running and self._container is not None:
            try:
                self._container.stop()
            except docker.errors.APIError as e:
                self.logger.error('Failed to stop container:\n%s' % e)
                self._result = {'status': 'fail', 'msg': e}

    def cleanup(self):
        """
        Stops and removes temporary files.
        """
        self.stop()
        if self._container is not None:
            try:
                self._container.remove()
            except docker.errors.APIError as e:
                self.logger.error('Failed to remove container:\n%s' % e)
            self._container = None

    def is_running(self):
        """
        Checks with underlying runner if the current experiment is running.
        Otherwise it could: not be started, finished or failed.
        """
        if self._is_running:
            self._is_running = self._check_container_running()

            if not self._is_running:
                # Container finished since last check, fetch the result.
                self._fetch_result()

        return self._is_running

    def get_result(self):
        """
        Returns the result, that is: state, loss, and any extra data.
        """
        if self.is_running():
            return {'state': 'running'}
        else:
            return self._result

    def get_update(self):
        """
        Returns the latest update from the experiment.
        """
        if self._is_running and self._container is not None:
            try:
                logs = self._container.logs(stdout=True, stderr=True,
                                            tail=LOG_TAIL_ROWS)
                if isinstance(logs, (bytes, bytearray)):
                    logs = logs.decode()

            except Exception as e:
                logs = 'Failed to fetch logs.'

            self._last_update = {
                'container':  {
                    'name': self._container.name,
                    'id': self._container.short_id,
                    'logs': logs,
                    'results_folder': self._volume_root,
                }
            }

        return self._last_update

    def _start_container(self, image):
        """
        Starts a docker container and returns its handle.
        """
        try:
            runtime = try_key(self._queue_job['data'], '', 'docker', 'runtime')
            container = self._docker_client.containers.run(
                image=image,
                tty=False,
                detach=True,
                environment=self._get_environment(),
                runtime=runtime,
                log_config={'type': 'json-file'},
                stdout=True,
                stderr=True,
                volumes=self._volumes,
            )
            return container

        except (docker.errors.ContainerError,
                docker.errors.APIError,
                docker.errors.ImageNotFound) as e:
            self.logger.error('Failed to start container:\n%s' % e)
            self._result = {'status': 'fail', 'msg': e}
            return None

    def _get_environment(self):
        """
        Creates the Target Image enviroment from the enviroment set by
        the worker and the job. Raises ValueError if job_spec contains
        the wrong format.
        """
        env = []
        job_env = try_key(self._queue_job['data'], [], 'docker', 'environment')
        if isinstance(job_env, list):
            env.extend(job_env)
        elif isinstance(job_env, dict):
            for k, v in job_env.items():
                env.append('%s=%s' % (k, v))
        else:
            raise ValueError('Invalid environment in job spec: %s' % job_env)
        env.extend(self.worker_env)
        return env

    def _check_container_running(self):
        """
        Checks if the container is running or not.
        """
        if self._container is None:
            return False
        else:
            self._container.reload()
            return self._container.status == 'running'

    def _fetch_result(self):
        """
        After a container has finished. This method fetches the
        result from the container.
        """
        if self._container is None:
            self._result = {'state': 'fail'}

        else:
            docker_logs = self._container.logs(stdout=True, stderr=True)
            try:
                with open(os.path.join(self._volume_root, 'docker_log.txt'), 'ab') as f:
                    f.write(docker_logs)
            except:
                pass

            try:
                with open(os.path.join(self._volume_root, 'loss.json'), 'r') as f:
                    loss = json.load(f)
                    self._result = loss

            except:
                self.logger.error('Failed to read loss')
                self._result = {'state': 'fail', 'msg': 'Failed to read loss.'}

    def _setup_volumes(self):
        """
        Sets up the volumes on the host's end along with the paths for the
        volumes.
        """
        data = self._queue_job['data']

        # Results folder path on host
        results_folder = try_key(data, 'results', 'volumes', 'results')
        folder_name = 'run_%s' % datetime.utcnow().strftime('%Y-%m-%d_%H.%M.%S.%f')
        volume_root = os.path.join(results_folder, folder_name)

        # Ensure path is absolute
        volume_root = os.path.abspath(volume_root)
        os.makedirs(volume_root, exist_ok=True)

        # Folder paths
        out_folder = os.path.join(volume_root, 'out')
        in_file = os.path.join(volume_root, 'params.json')
        loss_file = os.path.join(volume_root, 'loss.json')
        docker_log = os.path.join(volume_root, 'docker_log.txt')

        # Make empty foldes and files
        os.mkdir(out_folder)
        open(loss_file, 'a').close()

        # Create params file
        with open(in_file, 'w') as f:
            json.dump(self._queue_job['parameters'], f)

        self._volumes = [
            '%s:/hyperdock' % volume_root,
        ]
        self._volume_root = volume_root

        # Get host data folder, ensure it is absolute
        host_data_folder = try_key(data, '', 'volumes', 'data')
        host_data_folder = os.path.abspath(host_data_folder)
        if host_data_folder is not '':
            self._volumes.append('%s:/data:ro' % host_data_folder)

        return self._volumes

    def __str__(self):
        return 'Experiment: %s' % self._queue_job


class MockExperiment(Experiment):
    """
    A mock experiment that doesn't actually run any experiment.
    It runs for one check then finishes. Returns a loss of 1.0.
    """

    def __init__(self, job, worker_env):
        super().__init__(job, worker_env)
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

    def cleanup(self):
        self.running = False
