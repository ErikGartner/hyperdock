from unittest import TestCase
from datetime import datetime, timedelta
import os

import docker

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.common.stability import *


class TestStability(HyperdockBaseTest):

    def test_tryd(self):
        tryd(self.docker.containers.list)

        # Invalid socket
        self.docker = client = docker.DockerClient(base_url='unix://var/run/docker0000.sock')

        with self.assertRaises(requests.exceptions.RequestException):
            tryd(self.docker.containers.list)
