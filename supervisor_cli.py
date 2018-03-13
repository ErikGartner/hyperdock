import click
from hyperdock.supervisor.supervisor import create_dockerized_experiment


def load_space(config_module):
    module_name = 'hyperdock.config.%s' % config_module
    mod = __import__(module_name, fromlist=[''])
    return mod.SPACE


@click.command()
@click.option('--name', help='Experiment name.')
@click.option('--image', help='Docker image containing the experiment code.')
@click.option('--config_module', help='Python module containing the Hyperopt parameter space.')
@click.option('--trials', default=10, help='Maximum number of trials')
@click.option('--mongo', default='mongo://localhost:27017/hyperdock/jobs', help='Mongodb for saving results')
def run_experiment(name, image, mongo, config_module, trials):
    space = load_space(config_module)
    create_dockerized_experiment(name, mongo, image, space, trials)


if __name__ == '__main__':
    run_experiment()
