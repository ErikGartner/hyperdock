#!/usr/bin/env python
import json

import click
from pymongo import MongoClient

from .worker import Worker
from ..common import utils


@click.command()
@click.option('--mongodb', default='mongodb://localhost:27017/hyperdock', help='The URI to the MongoDB.')
@click.option('--env', default='[]', help='Environment variables to set in the Target image. Use Docker list format.')
@click.option('--parallelism', default=1, help='Maximum number of simulteanous experiments running.')
def launch_worker(mongodb, env, parallelism):
    utils.setup_logging()

    # Create database connection
    database = MongoClient(mongodb).get_default_database()

    # Parse docker env
    docker_env = json.loads(env)
    if not isinstance(docker_env, list):
        raise ValueError('Environment must be in Docker list format.')

    # Start worker
    worker = Worker(database, docker_env, parallelism, utils.in_docker())
    worker.start()


if __name__ == '__main__':
    launch_worker()
