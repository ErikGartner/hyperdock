import tempfile
import os
import json
import time
import sys
import traceback

import docker


class Worker:

    def __init__(self, docker_client):
        self.docker_client = docker_client

    def execute(self, image, host_results_folder, host_data_folder,
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
        docker_log = os.path.join(volume_root, 'docker_log.txt')

        # Make empty foldes and files
        os.mkdir(out_folder)
        open(loss_file, 'a').close()

        # Create params file
        with open(in_file, 'w') as f:
            json.dump(hyperparams, f)

        # Launch container
        t = time.time()
        try:
            container = self.docker_client.containers.run(
                image=image,
                tty=False,
                detach=True,
                environment=json.loads(os.environ.get('HYPERDOCK_ENV', '[]')),
                runtime=docker_runtime,
                log_config={'type': 'json-file'},
                stdout=True,
                stderr=True,
                volumes=[
                    '%s:/data:ro' % host_data_folder,
                    '%s:/hyperdock' % os.path.join(host_results_folder, folder_name),
                ])

            container.wait()

        except (docker.errors.ContainerError, docker.errors.APIError,
                docker.errors.ImageNotFound) as e:
            print(e)

        with open(docker_log, 'ab') as f:
            f.write(container.logs(stdout=True, stderr=True))

        try:
            # Manually remove container since we want to be able to retreive logs.
            container.remove()
        except docker.errors.APIError as e:
            print('Error while removing docker container: %s' % e)

        # Time the execution
        tt = time.time() - t

        try:
            with open(loss_file, 'r') as f:
                loss = json.load(f)
        except:
            print('Failed to read results.')
            return dict(loss={'status': 'fail', 'loss':'inf'})

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

    print('Running container')
    print('Docker params: %s' % docker_params)
    print('Params: %s' % hyperparams)

    # Execute the experiment
    results = worker.execute(
        image=docker_params['image'],
        host_results_folder=os.environ.get('HYPERDOCK_RESULT_DIR'),
        host_data_folder=os.environ.get('HYPERDOCK_DATA_DIR'),
        hyperparams=hyperparams,
        docker_runtime=os.environ.get('HYPERDOCK_RUNTIME', '')
    )

    return results['loss']
