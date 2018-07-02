from unittest import TestCase
from datetime import datetime, timedelta

import mongomock

from hyperdock.worker.worker import Worker
from hyperdock.common.experiment import MockExperiment
from hyperdock.common.workqueue import WorkQueue


class TestWorker(TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.worker_env = []
        self.worker = Worker(self.db, self.worker_env)

    def test_register_worker(self):
        collection = self.db.workers
        self.assertEqual(collection.count(), 0, 'Not empty before start')

        self.worker._register_worker()
        self.assertEqual(collection.count(), 1, 'Failed to register worker')

        self.assertEqual(collection.find_one()['id'], self.worker.id, 'Incorrect id')
        self.assertAlmostEquals(collection.find_one()['time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))

    def test_start_experiments(self):
        collection = self.db.workers
        q = WorkQueue(self.db)
        q.add_job('parameter', {'docker': {'image': 'a_docker_image'}}, 'trial-1', 'trial-1-name')
        self.worker._start_new_experiments(experiment_cls=MockExperiment)
        self.assertEqual(len(self.worker.experiments), 1)

        exp = self.worker.experiments[0]

        # Two calls required to finish MockExperiment
        self.worker._monitor_experiments()
        self.worker._monitor_experiments()

        self.assertEqual(len(self.worker.experiments), 0)
        self.assertEqual(exp.get_result(), {'state': 'ok', 'loss': 1})
        self.assertAlmostEquals(self.db.workqueue.find_one(
                                {'_id': exp.id})['end_time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))
