#!/usr/bin/env python
import json
import logging
import sys
import traceback

import click
from pymongo import MongoClient

from .worker import Worker
from ..common import utils


@click.command()
@click.option('--mongodb', default='mongodb://localhost:27017/hyperdock', help='The URI to the MongoDB.')
@click.option('--env', default='[]', help='Environment variables to set in the Target image. Use Docker list format.')
@click.option('--parallelism', default=1, help='Maximum number of simulteanous experiments running.')
@click.option('--loglevel', default='INFO', help='Set the loglevel as a string, e.g. INFO')
def launch_worker(mongodb, env, parallelism, loglevel):
    utils.setup_logging(logging.getLevelName(loglevel))

    logger = logging.getLogger('Main')

    # Create database connection
    database = MongoClient(mongodb).get_default_database()

    # Parse docker env
    docker_env = json.loads(env)
    if not isinstance(docker_env, list):
        raise ValueError('Environment must be in Docker list format.')

    worker = Worker(database, docker_env, parallelism, utils.in_docker())

    try:
        # Start worker
        worker.start()
    except:
        logger.error('Fatal error: %s, %s' % (
            sys.exc_info()[0],
            traceback.print_exc
        ))
    finally:
        # Perform immediate shutdown of all experiments
        worker._shutdown()


if __name__ == '__main__':
    launch_worker()
