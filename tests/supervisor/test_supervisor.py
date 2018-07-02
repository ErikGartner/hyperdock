from unittest import TestCase
from datetime import datetime, timedelta

import mongomock

from hyperdock.supervisor.supervisor import Supervisor
from hyperdock.common.experiment import MockExperiment
from hyperdock.common.workqueue import WorkQueue
from hyperdock.common.trialqueue import TrialQueue


class TestSupervisor(TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.supervisor = Supervisor(self.db)

        collection = self.db.trialqueue
        # Default data
        collection.insert({
            'start_time': -1,
            'end_time': -1,
            'name': 'trial-name',
            'created_on': datetime.utcnow(),
            'priority': 1,
            'retries': 1,
            'data': {'docker': {'image': 'a_docker_image'}},
            'param_space': {
                'learning_rate': [0.1, 0.001],
                'solver': ['adam', 'adagrad'],
            },
        })

    def test_process_trials(self):
        collection = self.db.trialqueue
        self.assertEqual(collection.find({'start_time': -1}).count(), 1,
                         'Empty before start')

        self.supervisor._process_trials()
        self.assertEqual(collection.find({'start_time': -1}).count(), 0,
                         'Trials not dequeued before start')

        workq = self.db.workqueue
        self.assertEqual(workq.find({'start_time': -1}).count(), 4,
                         'Missing parameter combinations')
        self.assertEqual(workq.find({'parameters':
                                     {'learning_rate': 0.001,
                                      'solver': 'adagrad'}
                                     }).count(), 1,
                         'Missing parameter combination')

    def test_purge_old_workers(self):
        collection = self.db.workers
        collection.insert({'id': 'test-worker-old', 'time': datetime(year=1,
                                                                     month=1,
                                                                     day=1)})
        collection.insert({'id': 'test-worker-new', 'time': datetime.utcnow()})
        self.assertEqual(collection.find().count(), 2, 'Missing workers')

        self.supervisor._purge_old_workers()
        self.assertEqual(collection.find().count(), 1, 'Incorrect purge')
        self.assertEqual(collection.find({'id': 'test-worker-new'}).count(), 1,
                                         'Incorrect purge')

    def test_expand_parameter_space(self):
        space1 = {'a': [1, 2], 'b': 1}
        params1 = [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}]
        out_params = self.supervisor._expand_parameter_space(space1)
        self.assertEqual(len(params1), len(out_params))
        for p in params1:
            self.assertIn(p, out_params)

        space2 = [{'a': [1, 2], 'b': 1}, {'c': 1, 'b': 2}]
        params2 = [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'c': 1, 'b': 2}]
        out_params = self.supervisor._expand_parameter_space(space2)
        self.assertEqual(len(params2), len(out_params))
        for p in params2:
            self.assertIn(p, out_params)

    def test_retry_dead_job(self):
        workq = self.db.workqueue

        self.assertEqual(workq.find().count(), 0)
        self.supervisor._process_trials()
        self.assertEqual(workq.find().count(), 4)

        # Time out all jobs
        old_time = datetime.utcnow() - timedelta(minutes=300)
        workq.update_many({}, {'$set': {'last_update': old_time,
                                        'start_time': old_time,
                                        'worker': 'worker-1'}})

        self.supervisor._purge_dead_jobs()
        self.assertEqual(workq.find().count(), 5, 'Should have retried one job.')
