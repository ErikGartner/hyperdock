#!/usr/bin/env python
import logging

import click
from pymongo import MongoClient

from .supervisor import Supervisor
from ..common import utils


@click.command()
@click.option(
    "--mongodb",
    show_default=True,
    default="mongodb://localhost:27017/hyperdock",
    help="The URI to the MongoDB.",
)
@click.option(
    "--loglevel",
    show_default=True,
    default="INFO",
    help="Set the loglevel as a string, e.g. INFO",
)
def launch_supervisor(mongodb, loglevel):
    utils.setup_logging(logging.getLevelName(loglevel))
    database = MongoClient(mongodb).get_default_database()

    supervisor = Supervisor(database, utils.in_docker())
    supervisor.start()


if __name__ == "__main__":
    launch_supervisor()
