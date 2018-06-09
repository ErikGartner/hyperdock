from unittest import TestCase
from datetime import datetime, timedelta

import mongomock

from hyperdock.common.trialqueue import TrialQueue


class TestTrialQueue(TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.q = TrialQueue(self.db)
        self.collection = self.db.trialqueue

        # Default data
        self.trial_id = self.collection.insert({
            'start_time': -1,
            'end_time': -1,
            'created_on': datetime.utcnow(),
            'priority': 1,
            'param_space': {
                'learning_rate': [0.1, 0.001],
                'solver': ['adam', 'adagrad'],
            },
        })

    def test_next_trial(self):
        self.assertEqual(self.collection.find({'start_time': -1}).count(), 1)
        trial = self.q.next_trial()
        self.assertEqual(self.collection.find({'start_time': -1}).count(), 0,
                         'Work not dequeued.')
        self.assertEqual(self.q.next_trial(), None, 'Work queue not empty')

    def test_update_trials(self):
        wq = self.db.workqueue
        # Insert dummy job
        job_id = wq.insert({'trial': self.trial_id, 'end_time': -1})
        self.q.update_trials()

        # Test that update_trials doesn't do anything before all jobs are finished.
        self.assertEqual(wq.find({'end_time': -1}).count(), 1,
                         "Shouldn't finish trial before all jobs are done.")
        self.assertEqual(self.collection.find({'end_time': -1}).count(), 1,
                         "Shouldn't finish trial before all jobs are done.")

        # Set job finished
        wq.update({'_id': job_id}, {'$set': {'end_time': datetime.utcnow()}})
        self.assertEqual(wq.find({'end_time': -1}).count(), 0,
                         'All jobs should be finished.')

        # Call processing
        self.q.update_trials()

        self.assertEqual(self.collection.find({'end_time': -1}).count(), 0,
                         "Shouldn't finish trial before all jobs are done.")
