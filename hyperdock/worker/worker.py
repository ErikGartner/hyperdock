from threading import Thread
import logging
from time import sleep
import secrets
from datetime import datetime, timedelta
import platform
import sys

import docker

from ..common.stability import tryd, crash_analysis
from ..common.workqueue import WorkQueue, WORK_TIMEOUT
from ..common.experiment import Experiment
from hyperdock.version import __version__ as hyperdock_version

SLEEP_TIME = 15


class Worker(Thread):
    def __init__(
        self,
        mongodb,
        docker_env,
        parallelism=1,
        in_docker=False,
        privileged=False,
    ):
        super().__init__(name="Worker")

        self._mongodb = mongodb
        self._docker_client = docker.from_env()
        self.id = self._generate_id()
        self.host = self._get_hostname(in_docker)
        self._logger = logging.getLogger(self.id)
        self._running = False
        self._workqueue = WorkQueue(mongodb)
        self._experiments = []
        self._max_experiments = parallelism
        self._docker_env = docker_env
        self._in_docker = in_docker
        self._last_loop_finished = None
        self._privileged = privileged
        self._sleep_time = SLEEP_TIME

    def run(self):
        """
        Starts the main loop and catches all errors to do a small post mortem.
        """
        self._running = True
        try:
            self._run()
        except:
            print(crash_analysis(), file=sys.stderr, flush=True)
            self._shutdown()

    def _run(self):
        """
        The main loop of the worker.
        It does the following:
            - Update keep alive
            - Check for experiments to finish
            - Check for new work
        """
        self._logger.info("Started main loop")

        while self._running:
            self._last_loop_finished = datetime.now()
            self._register_worker()
            self._monitor_experiments()
            self._kill_orphans()
            self._start_new_experiments()
            sleep(self._sleep_time)

            diff = datetime.now() - self._last_loop_finished
            if diff > timedelta(seconds=0.5 * WORK_TIMEOUT):
                self._logger.warning(
                    "Loop time was dangerously long: %s" % diff
                )

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
            "id": self.id,
            "time": datetime.utcnow(),
            "parallelism": self._max_experiments,
            "jobs": [e.id for e in self._experiments],
            "env": self._docker_env,
            "host": self.host,
            "version": hyperdock_version,
        }
        self._mongodb.workers.update_one(
            {"id": self.id}, {"$set": data}, upsert=True
        )
        self._logger.debug("Alive message sent: {}".format(data))

    def _get_hostname(self, in_docker=False):
        """
        Fetches a user friendly hostname for the container
        """
        hostname = platform.node()

        if in_docker:
            # Determine container name
            try:
                with open("/proc/self/cgroup", "r") as f:
                    line = f.readline()

                id = line.rsplit("/", 1)[1].strip()
                name = self._docker_client.containers.get(id).name
                hostname = "({}) {}".format(name, hostname)
            except:
                self._logger.warning("Failed to fetch Worker's container name")

        return hostname

    def _monitor_experiments(self):
        """
        Monitor the status of the current experiments.
        Also checks to see if an experiment has been cancelled by the user.
        """
        running_exps = []
        for ex in self._experiments:
            self._update_experiment(ex)

            if self._workqueue.is_job_cancelled(ex.id):
                # Experiment was cancelled by user
                ex.cleanup()
                continue

            if ex.is_running():
                # Update the stay alive
                running_exps.append(ex)
            else:
                # Wrap up the finished experiment
                self._cleanup_experiment(ex)
        self._experiments = running_exps

    def _update_experiment(self, experiment):
        """
        Takes and experiment and updates the workqueue.
        """
        self._workqueue.update_job(experiment.id, experiment.get_update())

    def _cleanup_experiment(self, experiment):
        """
        Takes an ended experiment and updates the work queue.
        """
        res = experiment.get_result()
        experiment.cleanup()
        self._workqueue.finish_job(experiment.id, res)

    def _start_new_experiments(self, experiment_cls=Experiment):
        """
        If not the max concurrent number of experiments is reached,
        starta new experiment.
        """
        for i in range(self._max_experiments - len(self._experiments)):
            job = self._workqueue.assign_next_job(self.id)
            if job is None:
                break

            experiment = experiment_cls(
                job, self._docker_env, privileged=self._privileged
            )
            experiment.start()
            self._experiments.append(experiment)

    def _shutdown(self):
        """
        Performs an immediate but graceful shutdown of the worker and
        experiments. Note we do note mark job as finished so it will count
        as a dropped job to be requeued.
        """
        for ex in self._experiments:
            try:
                ex.cleanup()
            except:
                self._logger.error(
                    "Failed to stop experiment during shutdown: %s",
                    sys.exc_info()[0],
                )
        self._experiments = []

    def _generate_id(self):
        """
        Generates a unique worker id.
        """
        return "worker-%s" % secrets.token_hex(8)

    def _kill_orphans(self):
        """
        Looks for orphaned jobs on the machine and if found kills them.
        """
        try:
            containers = tryd(
                self._docker_client.containers.list, all=True, sparse=True
            )
            container_ids = [c.id for c in containers]
        except docker.errors.APIError as e:
            self._logger.warning("Failed to list containers: %s" % e)
            return 0

        orphans = self._workqueue.check_for_orphans(container_ids)
        for (docker_id, job_id) in orphans:
            try:
                self._logger.info(
                    "Orphan found: docker_id=%s, job_id=%s."
                    % (docker_id, job_id)
                )
                container = tryd(self._docker_client.containers.get, docker_id)
                if container is not None:
                    self._logger.info(
                        "Orphan state=%s, trying to kill it."
                        % (container.status)
                    )
                    tryd(container.kill)
                    tryd(container.remove, force=True)
            except docker.errors.APIError as e:
                self._logger.error("Failed to kill %s: %s" % (docker_id, e))
            finally:
                self._workqueue.not_orphaned(job_id)

        return len(orphans)

    def __str__(self):
        return self.id
