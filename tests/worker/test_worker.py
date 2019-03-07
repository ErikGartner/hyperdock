from unittest import TestCase, mock
from datetime import datetime, timedelta
import platform

import mongomock
import docker

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.worker.worker import Worker
from ..common.mockexperiment import MockExperiment
from hyperdock.common.workqueue import WorkQueue
from hyperdock import version


class TestWorker(HyperdockBaseTest):
    def test_run(self):
        """
        test worker.run()
        """
        self.worker._run = mock.MagicMock()
        self.worker._shutdown = mock.MagicMock()

        self.assertFalse(
            self.worker._running, "Worker should not be marked as running before start"
        )

        self.worker.run()
        self.worker._run.assert_called()

    def test_error_in_run(self):
        """
        worker.run() should call _shutdown on error
        this should call _shutdown
        """
        self.worker._run = mock.MagicMock(side_effect=Exception())
        self.worker._shutdown = mock.MagicMock()

        self.worker.run()
        self.worker._shutdown.assert_called()

    def test_run_loop_and_stopping(self):
        """
        test worker run loop and stopping it
        """
        self.worker._sleep_time = 0.1
        self.worker._register_worker = mock.MagicMock()
        self.worker._monitor_experiments = mock.MagicMock()
        self.worker._kill_orphans = mock.MagicMock()
        self.worker._start_new_experiments = mock.MagicMock()
        self.worker._shutdown = mock.MagicMock()

        self.worker.start()
        self.assertTrue(
            self.worker._running, "Worker be should start when running thread"
        )

        self.worker._register_worker.assert_called_with()
        self.worker._monitor_experiments.assert_called_with()
        self.worker._kill_orphans.assert_called_with()
        self.worker._start_new_experiments.assert_called_with()

        self.worker.stop()
        self.worker.join(15)

        self.assertFalse(self.worker.is_alive(), "Thread should have exited")
        self.worker._shutdown.assert_called_with()
        self.assertFalse(
            self.worker._running, "Worker should be marked as not running after stopped"
        )

    def test_register_worker(self):
        """
        test registering of active worker
        """
        collection = self.db.workers
        self.assertEqual(collection.count(), 0, "Not empty before start")

        self.worker._register_worker()
        self.assertEqual(collection.count(), 1, "Failed to register worker")

        self.assertEqual(collection.find_one()["id"], self.worker.id, "Incorrect id")
        self.assertAlmostEquals(
            collection.find_one()["time"],
            datetime.utcnow(),
            msg="Timestamp off",
            delta=timedelta(seconds=5),
        )

        self.assertEqual(
            collection.find_one()["version"], version.__version__, "Incorrect version"
        )

    def test_start_experiments(self):
        """
        test start_experiment function in worker
        """
        collection = self.db.workers
        q = WorkQueue(self.db)
        q.add_job(
            "parameter",
            {"docker": {"image": "a_docker_image"}},
            "trial-1",
            "trial-1-name",
        )
        self.worker._start_new_experiments(experiment_cls=MockExperiment)
        self.assertEqual(len(self.worker._experiments), 1)

        exp = self.worker._experiments[0]

        # Two calls required to finish MockExperiment
        self.worker._monitor_experiments()
        self.worker._monitor_experiments()

        self.assertEqual(len(self.worker._experiments), 0)
        self.assertEqual(exp.get_result(), {"state": "ok", "loss": 1})
        self.assertAlmostEquals(
            self.db.workqueue.find_one({"_id": exp.id})["end_time"],
            datetime.utcnow(),
            msg="Timestamp off",
            delta=timedelta(seconds=5),
        )

    def test_kill_orphans(self):
        """
        test that worker kills orphaned jobs
        """

        # Start docker container
        self.experiment.start()
        self.container = self.experiment._container
        self.container.pause()
        self.container.reload()
        docker_id = self.container.id

        self.assertEqual(
            self.container.status, "paused", "Container must not have exited."
        )

        # Reset work queue
        self.work_col.remove({})

        # Set the connected job as orphaned
        self.job["orphaned"] = False
        self.job["update"] = {"container": {"long_id": docker_id}}
        self.work_col.insert(self.job)

        self.assertEqual(
            self.worker._kill_orphans(), 0, "Should not kill any containers"
        )

        # Reset work queue
        self.work_col.remove({})

        # Set the connected job as orphaned
        self.job["orphaned"] = True
        self.job["update"] = {"container": {"long_id": docker_id}}
        self.work_col.insert(self.job)

        self.assertEqual(self.worker._kill_orphans(), 1, "Should kill the container")
        with self.assertRaises(docker.errors.NotFound):
            self.docker.containers.get(docker_id)

    def test_shutdown(self):
        """
        test worker.shudown()
        """
        self.experiment.cleanup = mock.MagicMock()
        self.worker._experiments = [self.experiment]

        self.worker._shutdown()

        self.experiment.cleanup.assert_called()

    def test_get_hostname(self):
        """
        test resolving worker name
        """
        name = self.worker._get_hostname()
        self.assertEqual(name, platform.node())
