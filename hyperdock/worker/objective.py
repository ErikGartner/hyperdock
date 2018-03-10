import tempfile
import os
import json
import time

import docker


class Worker:

    def __init__(self, docker_client):
        self.docker_client = docker_client

    def execute(self, image, cmd, host_results_folder, host_data_folder,
                hyperparams, docker_runtime=''):
        """
        Executes the given image and waits for it to finish.
        Returns the loss of the execution.

        Args:
            image (string): The Docker image to execute.
            cmd (string): The command to send to the docker image.
            data_folder (tring): The folder containing the data for evaluated function.
            results_folder (string): Path to the base of the results folder.
            hyperparams (dict): The parameters for the function being optimized.

        Returns:
            dict: Containing the loss information for HyperOpt.
        """
        # Prepare mounts through attached volume to the worker.
        folder_name = 'run_%s' % time.strftime('%Y-%m-%d_%H.%M.%S')
        volume_root = os.path.join('/results', folder_name)
        os.mkdir(volume_root)

        # Folder paths
        out_folder = os.path.join(volume_root, 'out')
        in_file = os.path.join(volume_root, 'params.json')
        loss_file = os.path.join(volume_root, 'loss.json')

        # Make empty foldes and files
        os.mkdir(out_folder)
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
            runtime=docker_runtime,
            volumes=[
                '%s:/data:ro' % host_data_folder,
                '%s:/hyperdock' % os.path.join(host_results_folder, folder_name),
            ])

        print('Running container %s' % container.name)
        print('Params: %s' % hyperparams)
        t = time.time()
        container.wait()
        tt = time.time() - t

        try:
            with open(loss_file, 'r') as f:
                loss = json.load(f)
        except:
            raise Exception('Failed to read results.')

        print('Container finished with loss: %s!' % loss)
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
        host_results_folder=os.environ.get('HYPERDOCK_RESULT_DIR'),
        host_data_folder=os.environ.get('HYPERDOCK_DATA_DIR'),
        hyperparams=hyperparams,
        docker_runtime=os.environ.get('HYPERDOCK_RUNTIME', '')
    )

    return results['loss']
