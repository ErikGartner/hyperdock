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
        return_value = 'some-api-response'
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
        self.docker = client = docker.DockerClient(base_url='unix://var/run/docker0000.sock')

        with self.assertRaises(requests.exceptions.RequestException,
                               msg='Should throw error after failed retries!'):
            tryd(self.docker.containers.list)

    def test_trym(self):
        trym(self.db.workqueue.find, {})

        # # Invalid socket test, very slow!
        # self.db = MongoClient('localhost', 11111).hyperdock
        # with self.assertRaises(pymongo.errors.PyMongoError):
        #     trym(self.db.workqueue.insert, {'a': 'b'})

    def test_print_crash_analysis(self):
        # Make sure it doesn't contain any syntax errors
        print_crash_analysis()
