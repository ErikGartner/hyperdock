from unittest import TestCase, mock
from datetime import datetime, timedelta

import mongomock

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.supervisor.supervisor import Supervisor
from ..common.mockexperiment import MockExperiment
from hyperdock.common.workqueue import WorkQueue
from hyperdock.common.trialqueue import TrialQueue


class TestSupervisor(HyperdockBaseTest):
    def setUp(self):
        super().setUp()

    def test_start(self):
        """
        test the main loop of the supervisor
        """

        self.supervisor._purge_old_workers = mock.MagicMock()
        self.supervisor._process_trials = mock.MagicMock()
        self.supervisor._trialqueue.update_trials = mock.MagicMock()
        self.supervisor._purge_dead_jobs = mock.MagicMock()

        self.assertFalse(
            self.supervisor._running,
            "Supervisor should not be marked as running before started",
        )

        # Start thread
        self.supervisor._sleep_time = 1
        self.supervisor.start()

        self.assertTrue(
            self.supervisor.is_alive(), "Supervisor should be running"
        )
        self.assertTrue(
            self.supervisor._running, "Supervisor should be marked as running"
        )

        self.supervisor._purge_old_workers.assert_called()
        self.supervisor._process_trials.assert_called()
        self.supervisor._trialqueue.update_trials.assert_called()
        self.supervisor._purge_dead_jobs.assert_called()

        self.supervisor._running = False

    def test_stop(self):
        """
        test stopping supervisor
        """

        self.supervisor._purge_old_workers = mock.MagicMock()
        self.supervisor._process_trials = mock.MagicMock()
        self.supervisor._trialqueue.update_trials = mock.MagicMock()
        self.supervisor._purge_dead_jobs = mock.MagicMock()

        # Start thread
        self.supervisor._sleep_time = 1
        self.supervisor.start()

        self.assertTrue(
            self.supervisor._running, "Supervisor should be running"
        )

        self.supervisor.stop()
        self.supervisor.join(20)
        self.assertFalse(
            self.supervisor.is_alive(), "Supervisor should have stopped"
        )
        self.assertFalse(
            self.supervisor._running,
            "Supervisor should not be marked as running",
        )

    def test_process_trials(self):
        """
        test process_trials method

        should dequeue the oldest non-processed trial and create
        jobs from it and add those to the workqueue
        """
        collection = self.trial_col

        # Reset workqueue
        self.work_col.remove({})

        self.assertEqual(
            collection.find({"start_time": -1}).count(), 1, "Empty before start"
        )

        self.supervisor._process_trials()
        self.assertEqual(
            collection.find({"start_time": -1}).count(),
            0,
            "Trials not dequeued before start",
        )

        workq = self.db.workqueue
        self.assertEqual(
            workq.find({"start_time": -1}).count(),
            4,
            "Missing parameter combinations",
        )
        self.assertEqual(
            workq.find(
                {"parameters": {"learning_rate": 0.001, "solver": "adagrad"}}
            ).count(),
            1,
            "Missing parameter combination",
        )

    def test_purge_old_workers(self):
        """
        test purge_old_workers method

        should remove time-out workers from the worker collection
        """
        collection = self.db.workers
        collection.insert(
            {"id": "test-worker-old", "time": datetime(year=1, month=1, day=1)}
        )
        collection.insert({"id": "test-worker-new", "time": datetime.utcnow()})
        self.assertEqual(collection.find().count(), 2, "Missing workers")

        self.supervisor._purge_old_workers()
        self.assertEqual(collection.find().count(), 1, "Incorrect purge")
        self.assertEqual(
            collection.find({"id": "test-worker-new"}).count(),
            1,
            "Incorrect purge",
        )

    def test_retry_dead_job(self):
        """
        test retrying of dead jobs

        jobs that have timed out should be retried given enough tickets
        """
        # Reset self.work_col
        self.work_col.remove({})

        self.assertEqual(self.work_col.find().count(), 0)
        self.supervisor._process_trials()
        self.assertEqual(self.work_col.find().count(), 4)

        # Time out all jobs
        old_time = datetime.utcnow() - timedelta(minutes=300)
        self.work_col.update_many(
            {},
            {
                "$set": {
                    "last_update": old_time,
                    "start_time": old_time,
                    "worker": "worker-1",
                }
            },
        )

        self.supervisor._purge_dead_jobs()
        self.assertEqual(
            self.work_col.find().count(), 5, "Should have retried one job."
        )
        self.assertEqual(
            self.work_col.find({"cancelled": True, "orphaned": True}).count(),
            4,
            "Should have marked jobs as cancelled and orphaned",
        )

    def test_cancel_abandoned_jobs(self):
        """
        test cancelling jobs when the trials become invalid

        jobs that have timed out should be retried given enough tickets
        """
        self.assertEqual(self.work_col.find().count(), 1)

        # Finish trial
        self.trial_col.update({'_id': self.trial_id}, {"$set": {"end_time": 1}})

        self.supervisor._cancel_abandoned_jobs()

        self.assertEqual(
            self.work_col.find(
                {"cancelled": True, "end_time": {"$ne": -1}}
            ).count(),
            1,
            "Should have marked jobs as cancelled",
        )
