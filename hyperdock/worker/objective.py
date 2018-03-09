import tempfile
import os
import json
import time

import docker


class Worker:

    def __init__(self, docker_client):
        self.docker_client = docker_client

    def execute(self, image, cmd, results_folder, hyperparams):
        """
        Executes the given image and waits for it to finish.
        Returns the loss of the execution.

        Args:
            image (string): The Docker image to execute.
            cmd (string): The command to send to the docker image.
            results_folder (string): Path to the base of the results folder.
            hyperparams (dict): The parameters for the function being optimized.

        Returns:
            dict: Containing the loss information for HyperOpt.
        """
        # Prepare mounts
        volume_root = os.path.abspath(tempfile.mkdtemp(
            prefix='run_', dir='/results')
        )

        # Folder paths
        out_folder = os.path.join(volume_root, 'out')
        data_folder = os.path.join(volume_root, 'data')
        in_file = os.path.join(volume_root, 'params.json')
        loss_file = os.path.join(volume_root, 'loss.json')

        # Make empty foldes and files
        os.mkdir(out_folder)
        os.mkdir(data_folder)
        open(loss_file, 'a').close()

        # Create params file
        with open(in_file, 'w') as f:
            json.dump(hyperparams, f)

        # Launch container
        container = self.docker_client.containers.run(
            image=image,
            command=cmd,
            auto_remove=True,
            tty=True,
            detach=True,
            volumes=[
                '%s:/hyperdock:' % os.path.join(results_folder, volume_root.split('/', maxsplit=2)[-1]),
            ])

        print('Waiting for container: %s' % container.name)
        t = time.time()
        container.wait()
        tt = time.time() - t
        print('Container finished!')

        try:
            with open(loss_file, 'r') as f:
                loss = json.load(f)
        except:
            raise Exception('Failed to read results.')

        return dict(loss=loss, time=tt)


def parse_arguments(args):
    return (args['docker_params'], args['hyperparams'])


def docker_objective(args):

    # Get config
    docker_params, hyperparams = parse_arguments(args)

    # Create a Docker worker
    worker = Worker(
            docker_client=docker.from_env()
    )

    # Execute the experiment
    results = worker.execute(
        image=docker_params['image'],
        cmd=docker_params['cmd'],
        results_folder=os.environ.get('HYPERDOCK_RESULT_DIR'),
        hyperparams=hyperparams
    )

    return results['loss']
