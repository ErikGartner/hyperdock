from unittest import TestCase, skip
from datetime import datetime, timedelta
from time import sleep
import tempfile
import shutil
import os
import json
import platform

import docker

import mongomock

from hyperdock.common.experiment import Experiment
from hyperdock.common.trialqueue import TrialQueue
from hyperdock.supervisor.supervisor import Supervisor
from hyperdock.worker.worker import Worker
from .common.mockexperiment import MockExperiment
from hyperdock.common.workqueue import WorkQueue
from hyperdock.common.trialqueue import TrialQueue


class HyperdockBaseTest(TestCase):
    """
    This super class provides support for setting up the Hyperdock
    testing environment with Docker, mongo and default test data.
    It also tear downs these automatically.
    """

    def setUp(self):
        self.setup_mongo()
        self.setup_worker()
        self.setup_supervisor()
        self.setup_docker()
        self.setup_trialqueue()
        self.setup_workqueue()

        self.fill_default_data()

    def setup_mongo(self):
        self.db = mongomock.MongoClient().db

    def setup_worker(self):
        self.worker_env = ["WORKER_ID=1", "WORKER_ENV_OK=1"]
        self.worker = Worker(self.db, self.worker_env)

    def setup_supervisor(self):
        self.supervisor = Supervisor(self.db)

    def setup_docker(self):
        self.docker = docker.from_env()
        self.image = "erikgartner/hyperdock-demo:latest"

        # Fix issue with the tmp dir on macos
        dir = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
        self.test_folder = tempfile.mkdtemp(
            prefix="hyperdock-unittest-result-folder", dir="/tmp"
        )

    def setup_trialqueue(self):
        self.trialq = TrialQueue(self.db)
        self.trial_col = self.db.trialqueue

    def setup_workqueue(self):
        self.workqueue = WorkQueue(self.db)
        self.work_col = self.db.workqueue

    def fill_default_data(self):
        self.parameters = {"learning_rate": 0.1, "solver": "adam"}

        self.param_space = {
            "learning_rate": [0.1, 0.001],
            "solver": ["adam", "adagrad"],
        }

        self.data = {
            "docker": {"image": self.image, "environment": ["NVIDIA_VISIBLE_DEVICES="]},
            "volumes": {"results": self.test_folder},
        }

        self.trial_name = "trial-name-1"
        self.trial_id = self.trial_col.insert(
            {
                "name": self.trial_name,
                "start_time": -1,
                "end_time": -1,
                "created_on": datetime.utcnow(),
                "data": {"docker": {"image": self.image}},
                "priority": 1,
                "retries": 1,
                "param_space": self.param_space,
            }
        )

        self.worker_name = "worker-1"

        self.job = {
            "created_on": datetime.utcnow(),
            "start_time": -1,
            "end_time": -1,
            "data": self.data,
            "parameters": self.parameters,
            "worker": None,
            "last_update": -1,
            "priority": 1,
            "result": {},
            "trial": self.trial_id,
            "trial_name": self.trial_name,
            "cancelled": False,
            "orphaned": False,
            "update": {},
        }

        self.job_id = self.work_col.insert(self.job)
        self.experiment = Experiment(self.job, self.worker_env)
        self.container = None

    def tearDown(self):
        if self.container is not None:
            try:
                self.container.remove(force=True)
            except docker.errors.NotFound:
                pass
        shutil.rmtree(self.test_folder)
