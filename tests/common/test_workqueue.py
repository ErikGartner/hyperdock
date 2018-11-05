from unittest import TestCase
from datetime import datetime, timedelta

import mongomock

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.common.workqueue import WorkQueue, WORK_TIMEOUT


class TestWorkQueue(HyperdockBaseTest):

    def setUp(self):
        super().setUp()

    def test_add_job(self):
        self.assertEqual(self.work_col.count(), 1, 'Failed to add to queue')
        self.assertEqual(self.work_col.find_one()['parameters'], self.parameters,
                         'Incorrect parameters')
        self.assertAlmostEquals(self.work_col.find_one()['created_on'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))
        self.assertEqual(self.work_col.find_one()['start_time'],
                         -1, msg='Timestamp off',)
        self.assertEqual(self.work_col.find_one()['end_time'],
                         -1, msg='Timestamp off',)
        self.assertEqual(self.work_col.find_one()['last_update'],
                         -1, msg='Timestamp off',)

        job = self.work_col.find_one()
        self.assertEqual(job['trial'], self.trial_id, msg='Incorrect trial id')
        self.assertEqual(job['trial_name'], self.trial_name, msg='Incorrect trial name')

    def test_take_job(self):
        worker_id = 'worker1'
        job = self.workqueue.assign_next_job(worker_id)

        self.assertEqual(job['parameters'], self.parameters)
        self.assertEqual(job['worker'], worker_id)
        self.assertAlmostEquals(job['start_time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))
        self.assertAlmostEquals(job['last_update'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))

        result = 'result1'
        self.workqueue.finish_job(job['_id'], result)

        self.assertEqual(self.work_col.find_one({'_id': job['_id']})['result'], result,
                         'Failed to add result')
        self.assertAlmostEquals(self.work_col.find_one({'_id': job['_id']})['end_time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))

    def test_is_job_cancelled(self):
        self.assertFalse(self.workqueue.is_job_cancelled(self.job_id))
        self.work_col.update({'_id': self.job_id},
                               {'$set': {'cancelled': True,
                                         'end_time': datetime.utcnow()}})
        self.assertTrue(self.workqueue.is_job_cancelled(self.job_id))

    def test_purge_dead_jobs(self):
        res = self.workqueue.purge_dead_jobs()
        self.assertEqual(list(res), [])
        self.assertEqual(self.work_col.find({'cancelled': True}).count(), 0, 'Should not purge new jobs')

        t = datetime.utcnow()
        self.work_col.update_one({'_id': self.job_id}, {'$set': {'start_time': t, 'last_update': t}})
        res = self.workqueue.purge_dead_jobs()
        self.assertEqual(res, [])
        self.assertEqual(self.work_col.find({'cancelled': True}).count(), 0, 'Should not purge active jobs')

        job2 = self.workqueue.add_job(self.parameters, self.data, 'trial2', 'trial2-name')

        t = datetime.utcnow() - timedelta(minutes=(WORK_TIMEOUT + 1))
        self.work_col.update_one({'_id': self.job_id}, {'$set': {'start_time': t, 'last_update': t}})
        self.work_col.update_one({'_id': job2}, {'$set': {'start_time': t, 'last_update': t}})

        res = self.workqueue.purge_dead_jobs()
        self.assertEqual(self.work_col.find({'cancelled': True}).count(), 2, 'Should purge dead jobs')
        self.assertEqual(res[0]['cancelled'], True)
        self.assertEqual(res[0]['result']['state'], 'fail')
        self.assertEqual(len(res), 2, 'Should find and return 2 dead jobs.')

    def test_orphan_handling(self):
        docker_id = '123'

        # Reset work queue
        self.work_col.remove({})

        # Add non-orphaned job
        self.job['orphaned'] = False
        self.job['update'] = {
            'container':  {
                'long_id': docker_id,
            }
        }
        self.work_col.insert(self.job)

        self.assertEqual(len(self.workqueue.check_for_orphans([docker_id])),
                         0, "Shouldn't report as orphan")

        # Reset work queue
        self.work_col.remove({})

        # Add orphaned job
        self.job['orphaned'] = True
        self.job['update'] = {
            'container':  {
                'long_id': docker_id,
            }
        }
        self.work_col.insert(self.job)

        orphans = self.workqueue.check_for_orphans([docker_id])
        self.assertEqual(len(orphans), 1, "Should report as orphan")


        self.workqueue.not_orphaned(orphans[0][1])
        self.assertEqual(len(self.workqueue.check_for_orphans([docker_id])),
                         0, "Shouldn't report as orphan")
