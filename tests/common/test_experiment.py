from unittest import TestCase, skip, mock
from datetime import datetime, timedelta
from time import sleep
from tempfile import mkdtemp
import shutil
import os
import json

import docker
import requests

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.common.experiment import Experiment


class TestExperiment(HyperdockBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_start_container(self):
        """
        test start_container works with Docker API
        """
        self.container = self.experiment._start_container(self.image)
        self.assertIsNotNone(self.container, "Error starting container")

        self.container.wait(timeout=10)
        self.container.reload()
        self.assertEqual(self.container.status, "exited", "Container did not exit")

    def test_start(self):
        """
        test experiment.start()
        essentially start() calls many other private methods making this
        unit test almost an integration test.
        """
        self.experiment.start()
        self.container = self.experiment._container

        self.assertTrue(self.experiment.is_running(), "Container didnt start")

        # Ensure correct image
        self.assertTrue(
            self.image in str(self.experiment._container.image), "Incorrect image"
        )

        self.assertTrue(
            self.experiment._volume_root.startswith(self.test_folder),
            "Incorrect result folder",
        )

        # Check enviroment variables
        for e in self.job["data"]["docker"]["environment"]:
            self.assertIn(e, self.container.attrs["Config"]["Env"], "Missing job env")
        for e in self.worker_env:
            self.assertIn(
                e, self.container.attrs["Config"]["Env"], "Missing worker env"
            )

        # Check that update fetches information
        update = self.experiment.get_update()
        self.assertIn("container", update)
        self.assertTrue(isinstance(update["container"]["logs"], str))

        # Ensure the result folder contains trial name and id
        self.assertTrue(
            "/%s-%s/" % (self.job["trial_name"], self.job["trial"])
            in self.experiment._volume_root,
            "Result folder doesnt contain trial name and id",
        )

        # Wait for container to exit
        self.container.wait(timeout=10)

        # Make sure it says it has has stopped
        self.assertFalse(self.experiment.is_running(), "Container has stopped")

        # Check parameters were correct
        with open(os.path.join(self.experiment._volume_root, "params.json"), "r") as f:
            params = json.load(f)
            self.assertDictEqual(
                params, self.job["parameters"], "Incorrect parameters!"
            )

        # Get result, ensure it is correct
        result = self.experiment.get_result()
        self.assertDictEqual(result, {"state": "ok", "loss": 0})

        # Ensure the container still exists in a stopped format
        self.container.reload()
        self.assertEqual(self.container.status, "exited", "Container had not stopped")

        # Test the graph reading
        graph_list = self.experiment._read_graphs()
        self.assertEqual(len(graph_list), 1)
        graph = graph_list[0]
        self.assertIn("name", graph)
        self.assertIn("series", graph)
        self.assertListEqual(graph_list, self.experiment._graphs)

        # Clean up and make sure it is removed
        self.experiment.cleanup()
        with self.assertRaises(docker.errors.NotFound):
            self.container.reload()
        self.container = None

        self.assertIsNone(self.experiment._container)

        with self.assertRaises(RuntimeError):
            self.experiment.start()

    def test_stop(self):
        """
        test stopping of running experiment
        """
        self.experiment.start()
        self.container = self.experiment._container

        # Mock the stop function in the Docker API
        stop_function = self.container.stop
        self.container.stop = mock.MagicMock()
        self.experiment._fetch_result = mock.MagicMock()

        self.experiment.stop()
        # Checks that stop is called on container
        self.container.stop.assert_called()
        # Check that stop fetches results from container
        self.experiment._fetch_result.assert_called()

        # Stop real container
        stop_function()

    def test_cleanup(self):
        """
        test experiment.cleanup()
        """
        self.experiment.start()
        self.container = self.experiment._container

        remove_function = self.container.remove
        self.container.remove = mock.MagicMock()
        self.experiment.cleanup()

        # Ensure remove function was called
        self.container.remove.assert_called_with(force=True)

        self.assertFalse(
            self.experiment._is_running,
            "Experiment should not be running after cleanup",
        )

        remove_function()

    def test_invalid_image(self):
        """
        ensure starting invalid Docker image fails gracefully
        """
        self.job["data"]["docker"]["image"] = "NONE_EXISTANT_IMAGE"
        experiment = Experiment(self.job, self.worker_env)
        experiment.start()

        self.assertFalse(experiment.is_running(), "Should not start.")
        self.assertEqual(
            experiment.get_result()["state"], "fail", "Should have failed."
        )

    def test_docker_daemon_down(self):
        """
        ensure that starting experiment without Docker daemon fails
        correctly
        """
        down_docker = docker.DockerClient(base_url="tcp://127.0.0.1:9999")
        self.experiment._docker_client = down_docker

        with self.assertRaises(requests.exceptions.RequestException):
            self.experiment.start()
        self.assertFalse(self.experiment.is_running(), "Should not start.")
        self.assertEqual(
            self.experiment.get_result()["state"], "fail", "Should have failed."
        )

    def test_cancel_experiment(self):
        """
        test experiment cancelling
        """
        self.experiment.start()
        self.container = self.experiment._container

        self.experiment._fetch_result()

        # Cancel experiment by calling cleanup directly
        self.experiment.cleanup()
        self.container = self.experiment._container

        # Assert that Docker log was written
        log_path = os.path.join(self.experiment._volume_root, "docker_log.txt")
        self.assertTrue(os.path.isfile(log_path))

    def test_handling_of_removed_container(self):
        """
        test handling of externally removed container
        """
        self.experiment.start()
        self.container = self.experiment._container
        self.assertTrue(self.experiment.is_running())

        self.container.remove(force=True)
        self.assertFalse(self.experiment.is_running())

        self.experiment.cleanup()
        self.assertEqual(self.experiment.get_result()["state"], "fail")
        self.container = None

    def test_privileged(self):
        """
        test starting job as privileged container
        """
        self.experiment._privileged = True
        self.experiment.start()
        self.container = self.experiment._container
        self.container.reload()
        self.assertTrue(
            self.container.attrs["HostConfig"]["Privileged"],
            "Container was not started as privileged!",
        )

    def test_not_privileged(self):
        """
        test starting job as not privileged container
        """
        self.experiment.start()
        self.container = self.experiment._container
        self.container.reload()
        self.assertFalse(
            self.container.attrs["HostConfig"]["Privileged"],
            "Container was started as privileged!",
        )

    def test_get_environment(self):
        """
        test environment variables to be set in the container.
        """
        # List format
        worker_env = self.experiment._worker_env
        self.experiment._queue_job["data"]["docker"]["environment"] = ["A=B", "C=2"]
        res = self.experiment._get_environment()
        self.assertSetEqual(
            set(res),
            set(worker_env + ["A=B", "C=2"]),
            "Environment doesn't contain correct variables",
        )

        # Dict format
        self.experiment._queue_job["data"]["docker"]["environment"] = {"A": "B", "C": 2}
        res = self.experiment._get_environment()
        self.assertSetEqual(
            set(res),
            set(worker_env + ["A=B", "C=2"]),
            "Environment doesn't contain correct variables",
        )

        with self.assertRaises(ValueError):
            # Should throw error on invalid data type. Should be list/dict
            self.experiment._queue_job["data"]["docker"]["environment"] = 123
            res = self.experiment._get_environment()
