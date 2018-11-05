from unittest import TestCase
from datetime import datetime, timedelta

import mongomock
import docker

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.worker.worker import Worker
from hyperdock.common.experiment import MockExperiment
from hyperdock.common.workqueue import WorkQueue
from hyperdock import version


class TestWorker(HyperdockBaseTest):

    def test_register_worker(self):
        collection = self.db.workers
        self.assertEqual(collection.count(), 0, 'Not empty before start')

        self.worker._register_worker()
        self.assertEqual(collection.count(), 1, 'Failed to register worker')

        self.assertEqual(collection.find_one()['id'], self.worker.id, 'Incorrect id')
        self.assertAlmostEquals(collection.find_one()['time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))

        self.assertEqual(collection.find_one()['version'], version.__version__,
                         'Incorrect version')

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

    def test_kill_orphans(self):

        # Start docker container
        self.experiment.start()
        self.container = self.experiment._container
        self.container.pause()
        self.container.reload()
        docker_id = self.container.id

        self.assertEqual(self.container.status, 'paused', 'Container must not have exited.')

        # Reset work queue
        self.work_col.remove({})

        # Set the connected job as orphaned
        self.job['orphaned'] = False
        self.job['update'] = {
            'container':  {
                'long_id': docker_id,
            }
        }
        self.work_col.insert(self.job)

        self.assertEqual(self.worker._kill_orphans(), 0, 'Should not kill any containers')

        # Reset work queue
        self.work_col.remove({})

        # Set the connected job as orphaned
        self.job['orphaned'] = True
        self.job['update'] = {
            'container':  {
                'long_id': docker_id,
            }
        }
        self.work_col.insert(self.job)

        self.assertEqual(self.worker._kill_orphans(), 1, 'Should kill the container')
        with self.assertRaises(docker.errors.NotFound):
            self.docker.containers.get(docker_id)

    def test_shutdown(self):
        # Check for raised errors
        self.worker._shutdown()
