from unittest import TestCase
from datetime import datetime, timedelta

import mongomock

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.common.trialqueue import TrialQueue


class TestTrialQueue(HyperdockBaseTest):
    def setUp(self):
        super().setUp()

    def test_next_trial(self):
        """
        test dequeuing the next trial in the queue
        """
        self.assertEqual(self.trial_col.find({"start_time": -1}).count(), 1)
        trial = self.trialq.next_trial()
        self.assertEqual(
            self.trial_col.find({"start_time": -1}).count(),
            0,
            "Work not dequeued.",
        )
        self.assertEqual(self.trialq.next_trial(), None, "Work queue not empty")

    def test_update_trials(self):
        """
        test updating the state of the trials
        """

        self.trialq.update_trials()

        # Test that update_trials doesn't do anything before all jobs are finished.
        self.assertEqual(
            self.work_col.find({"end_time": -1}).count(),
            1,
            "Shouldn't finish trial before all jobs are done.",
        )
        self.assertEqual(
            self.trial_col.find({"end_time": -1}).count(),
            1,
            "Shouldn't finish trial before all jobs are done.",
        )

        # Set job finished
        self.work_col.update(
            {"_id": self.job_id}, {"$set": {"end_time": datetime.utcnow()}}
        )
        self.assertEqual(
            self.work_col.find({"end_time": -1}).count(),
            0,
            "All jobs should be finished.",
        )

        # Call processing
        self.trialq.update_trials()

        self.assertEqual(
            self.trial_col.find({"end_time": -1}).count(),
            0,
            "Shouldn't finish trial before all jobs are done.",
        )

    def test_use_retry_ticker(self):
        """
        test the retry ticket for a trial
        """
        self.assertTrue(
            self.trialq.use_retry_ticket(self.trial_id),
            "Should allow for retry",
        )
        self.assertEqual(
            self.trial_col.find_one({"_id": self.trial_id})["retries"],
            0,
            "Shouldn't have any retries left.",
        )
        self.assertFalse(
            self.trialq.use_retry_ticket(self.trial_id),
            "Should not allow for retry",
        )

    def test_get_live_trials(self):
        trials = self.trialq.get_live_trials()
        self.assertEqual(len(trials), 1, "Should have 1 live trial")
        self.assertEqual(type(trials), list)
