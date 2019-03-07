from unittest import TestCase, mock
from datetime import datetime, timedelta
import os

import docker
from pymongo import MongoClient

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.common.stability import *


class TestStability(HyperdockBaseTest):
    def test_tryd(self):
        """
        tryd function should call function
        """
        return_value = "some-api-response"
        docker_function = mock.MagicMock(return_value=return_value)
        result = tryd(docker_function)

        # Asserts that the API was actually called
        self.assertEqual(result, return_value)
        docker_function.assert_called_with()

    def test_tryd_error(self):
        """
        tryd should retry and throw errors
        """
        # Test with invalid Docker connection
        self.docker = client = docker.DockerClient(
            base_url="unix://var/run/docker0000.sock"
        )

        with self.assertRaises(
            requests.exceptions.RequestException,
            msg="Should throw error after failed retries!",
        ):
            tryd(self.docker.containers.list)

    def test_trym(self):
        """
        trym should call the function
        """
        return_value = "some-api-response"
        mongo_function = mock.MagicMock(return_value=return_value)
        result = trym(mongo_function, {})

        # Asserts that the API was actually called
        self.assertEqual(result, return_value)
        mongo_function.assert_called_with({})

    def test_trym_error(self):
        """
        trym should retry and throw error on failure
        """
        mongo_function = mock.MagicMock(side_effect=pymongo.errors.PyMongoError())

        with self.assertRaises(pymongo.errors.PyMongoError):
            trym(mongo_function, {})
        mongo_function.assert_called_with({})

    def test_retry(self):
        """
        retry should retry the functions n times then raise if still error
        """
        mock_func = mock.MagicMock(side_effect=NotImplementedError)

        with self.assertRaises(NotImplementedError):
            retry(mock_func, 2, 0.01, (NotImplementedError,), 13)
        mock_func.assert_called_with(13)
        self.assertEqual(mock_func.call_count, 3)

    def test_trym_error(self):
        """
        trym should retry and throw error on failure
        """
        pass

    def test_crash_analysis(self):
        """
        crash_analysis should return a string with system information

        Note this function is hard to test since it returns live information
        from the system.
        """
        msg = crash_analysis()
        self.assertRegexpMatches(msg, r"Time: \d+", "Should contain time stamp")
