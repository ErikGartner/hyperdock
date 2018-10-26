#!/usr/bin/env python
import click
from pymongo import MongoClient

from .supervisor import Supervisor
from ..common import utils


@click.command()
@click.option('--mongodb', default='mongodb://localhost:27017/hyperdock', help='The URI to the MongoDB.')
def launch_supervisor(mongodb):
    utils.setup_logging()
    database = MongoClient(mongodb).get_default_database()

    supervisor = Supervisor(database, utils.in_docker())
    supervisor.start()


if __name__ == '__main__':
    launch_supervisor()
