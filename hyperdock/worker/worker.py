import tempfile
import os

import docker


class Worker:

    def __init__(self):
        self.docker_client = docker.from_env()

    def execute(self, image, cmd, docker_params):
        """
        Executes the given image and waits for it to finish.
        Returns the loss of the execution.

        Args:
            image (string): The Docker image to execute.

        Returns:
            dict: Containing the loss information for HyperOpt.
        """
        # Prepare mounts
        volume_root = os.path.abspath(tempfile.mkdtemp(
            prefix='hyperdock-run_', dir='./data'))

        # Folder paths
        out_folder = os.path.join(volume_root, 'out')
        data_folder = os.path.join(volume_root, 'data')
        in_file = os.path.join(volume_root, 'in.json')
        loss_file = os.path.join(volume_root, 'loss.json')

        # Make empty foldes and files
        os.mkdir(out_folder)
        os.mkdir(data_folder)
        open(in_file, 'a').close()
        open(loss_file, 'a').close()


        # Launch container
        container = self.docker_client.containers.run(
            image,
            command=cmd,
            auto_remove=True,
            tty=True,
            detach=True,
            volumes=[
                '%s:/hyperdock:' % volume_root,
            ])

        print('Waiting for container: %s' % container.name)
        container.wait()
        print('Container finished!')

        return out_folder
