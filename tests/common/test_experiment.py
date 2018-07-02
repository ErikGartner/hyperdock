from unittest import TestCase, skip
from datetime import datetime, timedelta
from time import sleep
from tempfile import mkdtemp
import shutil
import os
import json

import docker

from hyperdock.common.experiment import Experiment


# @skip('since it requires a Docker installation')
class TestExperiment(TestCase):

    def setUp(self):
        self.docker = docker.from_env()
        self.image = 'erikgartner/hyperdock-test:latest'
        self.test_folder = mkdtemp(prefix='hyperdock-unittest-result-folder')

        self.job = {
            'created_on': datetime.utcnow(),
            'start_time': datetime.utcnow(),
            'end_time': -1,
            'data': {
                'docker': {
                    'image': self.image,
                    'environment': [
                        'NVIDIA_VISIBLE_DEVICES=1',
                    ],
                },
                'volumes': {
                    'results': self.test_folder,
                }
            },
            'parameters': {
                'a': 1,
                'b': 2,
            },
            'worker': 'worker-1',
            'last_update': -1,
            'priority': 1,
            'result': {},
            'trial': 'trial-1',
            'trial_name': 'ablation-trial-1',
            '_id': 'job-1',
        }
        self.worker_env = ['WORKER_ID=1', 'WORKER_ENV_OK=1']
        self.experiment = Experiment(self.job, self.worker_env)
        self.container = None

    def tearDown(self):
        if self.container is not None:
            self.container.remove(force=True)
        shutil.rmtree(self.test_folder)

    def test_start_container(self):
        self.container = self.experiment._start_container(self.image)
        self.assertIsNotNone(self.container, 'Error starting container')

        self.container.wait(timeout=10)
        self.container.reload()
        self.assertEqual(self.container.status, 'exited',
                         'Container had not stopped')

    def test_start(self):
        self.experiment.start()
        self.container = self.experiment._container

        # Make sure it has started. Not that if it exits quickly we might miss
        # it.
        self.assertTrue(self.experiment.is_running(), 'Container didnt start')

        # Ensure correct image
        self.assertTrue(self.image in str(self.experiment._container.image),
                        'Incorrect image')

        self.assertTrue(self.experiment._volume_root.startswith(self.test_folder),
                        'Incorrect result folder')

        # Check enviroment variables
        for e in self.job['data']['docker']['environment']:
            self.assertIn(e,
                          self.container.attrs['Config']['Env'],
                          'Missing job env')
        for e in self.worker_env:
            self.assertIn(e,
                          self.container.attrs['Config']['Env'],
                          'Missing worker env')

        # Check that update fetches information
        update = self.experiment.get_update()
        self.assertIn('container', update)
        self.assertTrue(isinstance(update['container']['logs'], str))

        # Ensure the result folder contains trial name and id
        self.assertTrue('/%s-%s/' % (self.job['trial_name'], self.job['trial'])
                        in self.experiment._volume_root, 'Result folder doesnt contain trial name and id')

        # Wait for container to exit
        self.container.wait(timeout=10)

        # Make sure it says it has has stopped
        self.assertFalse(self.experiment.is_running(), 'Container has stopped')

        # Check parameters were correct
        with open(os.path.join(self.experiment._volume_root,
                               'params.json'), 'r') as f:
            params = json.load(f)
            self.assertDictEqual(params, self.job['parameters'],
                                 'Incorrect parameters!')

        # Get result, ensure it is correct
        result = self.experiment.get_result()
        self.assertDictEqual(result, {'state': 'ok', 'loss': 0})

        # Ensure the container still exists in a stopped format
        self.container.reload()
        self.assertEqual(self.container.status, 'exited',
                         'Container had not stopped')

        # Clean up and make sure it is removed
        self.experiment.cleanup()
        with self.assertRaises(docker.errors.NotFound):
            self.container.reload()
        self.container = None

        self.assertIsNone(self.experiment._container)

        with self.assertRaises(RuntimeError):
            self.experiment.start()

    def test_invalid_image(self):
        self.job['data']['docker']['image'] = 'NONE_EXISTANT_IMAE'
        experiment = Experiment(self.job, self.worker_env)
        experiment.start()

        self.assertFalse(experiment.is_running(), 'Should not start.')
        self.assertEqual(experiment.get_result()['state'], 'fail', 'Should have failed.')

    def test_docker_daemon_down(self):
        down_docker = docker.DockerClient(base_url='tcp://127.0.0.1:9999')
        self.experiment._docker_client = down_docker

        self.experiment.start()
        self.assertFalse(self.experiment.is_running(), 'Should not start.')
        self.assertEqual(self.experiment.get_result()['state'], 'fail', 'Should have failed.')
