from unittest import TestCase
from datetime import datetime, timedelta
import os

import docker
from pymongo import MongoClient

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.common.stability import *


class TestStability(HyperdockBaseTest):

    def test_tryd(self):
        tryd(self.docker.containers.list)

        # Invalid socket
        self.docker = client = docker.DockerClient(base_url='unix://var/run/docker0000.sock')

        with self.assertRaises(requests.exceptions.RequestException):
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
