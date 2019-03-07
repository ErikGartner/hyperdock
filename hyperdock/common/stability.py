"""
The module contains functions used for stability and crash analysis.
"""
import logging
from time import sleep
import sys
import traceback
import datetime

import requests
import pymongo
import psutil
import docker

from .config import config

logger = logging.getLogger("stability")
cfg = config()


def tryd(func, *args, **kwargs):
    """
    Tries a Docker call that might fail due to underlying issues in the
    connectetion to the Daemon. After repeated failures the error is propagated.
    """
    return retry(
        func,
        cfg["STABILITY"]["RETRY"]["RETRIES"],
        cfg["STABILITY"]["RETRY"]["SLEEP_TIME"],
        (requests.exceptions.RequestException,),
        *args,
        **kwargs
    )


def trym(func, *args, **kwargs):
    """
    Tries a mongo operation that might fail due to underlying issues in the
    connectetion to the database. After repeated failures the error is propagated.
    """
    return retry(
        func,
        cfg["STABILITY"]["RETRY"]["RETRIES"],
        cfg["STABILITY"]["RETRY"]["SLEEP_TIME"],
        (pymongo.errors.PyMongoError,),
        *args,
        **kwargs
    )


def retry(func, nbr_retries, sleep_time, errors, *args, **kwargs):
    """
    Retries an instable and error prone function.
    """
    last_error = None
    while nbr_retries >= 0:
        try:
            return func(*args, **kwargs)
        except errors as e:
            logger.debug("Failed to call %s: %s" % (func, e))
            last_error = e
            nbr_retries -= 1

        sleep(sleep_time)

    logger.error("Function %s failed after several tries: %s" % (func, last_error))
    raise last_error


def crash_analysis():
    """
    This function gathers relevant data upon a worker crash.
    """

    msg = """
========= Crash Analysis =========
Time: {}
Last error:
{}
Stack trace:
{}
CPU usage:
{}
Memory usage:
{}
==================================
    """.format(
        datetime.datetime.now(),
        sys.exc_info()[0],
        traceback.print_exc(),
        psutil.cpu_percent(percpu=True),
        psutil.virtual_memory(),
    )
    return msg
