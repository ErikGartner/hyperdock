#!/usr/bin/env python
import os

import click
from pymongo import MongoClient

from .supervisor import Supervisor
from ..common import utils


@click.command()
@click.option('--mongodb', default='mongodb://localhost:27017/hyperdock', help='The URI to the MongoDB.')
def launch_supervisor(mongodb):
    utils.setup_logging()
    database = MongoClient(mongodb).get_default_database()

    # Checks to see if it is running in Docker
    in_docker = os.environ.get('HYPERDOCK_IN_DOCKER', 'false').lower() == 'true'

    supervisor = Supervisor(database, in_docker)
    supervisor.start()


if __name__ == '__main__':
    launch_supervisor()
