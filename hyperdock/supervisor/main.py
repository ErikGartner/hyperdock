#!/usr/bin/env python

import click
from pymongo import MongoClient

from .supervisor import Supervisor


@click.command()
@click.option('--mongodb', default='mongodb://localhost:27017/hyperdock', help='The URI to the MongoDB.')
def launch_supervisor(mongodb):
    database = MongoClient(mongodb).get_default_database()
    supervisor = Supervisor(database)
    supervisor.start()


if __name__ == '__main__':
    launch_supervisor()
