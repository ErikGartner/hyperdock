#!/usr/bin/env python
import json
import logging
import sys
import traceback
import os

import click
from pymongo import MongoClient

from .worker import Worker
from ..common import utils


@click.command()
@click.option(
    "--mongodb",
    show_default=True,
    default="mongodb://localhost:27017/hyperdock",
    help="The URI to the MongoDB.",
)
@click.option(
    "--env",
    default="[]",
    help="Environment variables to set in the Target image. Use Docker list format.",
)
@click.option(
    "--parallelism",
    show_default=True,
    default=1,
    type=int,
    help="Maximum number of simulteanous experiments running.",
)
@click.option(
    "--loglevel",
    show_default=True,
    default="INFO",
    help="Set the loglevel as a string, e.g. INFO",
)
@click.option(
    "--privileged", is_flag=True, help="Run experiments as privileged containers"
)
def launch_worker(mongodb, env, parallelism, loglevel, privileged):
    utils.setup_logging(logging.getLevelName(loglevel))

    logger = logging.getLogger("Main")

    # Create database connection
    database = MongoClient(mongodb).get_default_database()

    # Parse docker env
    docker_env = json.loads(env)
    if not isinstance(docker_env, list):
        raise ValueError("Environment must be in Docker list format.")

    worker = Worker(database, docker_env, parallelism, utils.in_docker(), privileged)
    worker.start()


if __name__ == "__main__":
    launch_worker()
