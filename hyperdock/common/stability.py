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

logger = logging.getLogger('stability')


def tryd(func, *args, **kwargs):
    """
    Tries a Docker call that might fail due to underlying issues in the
    connectetion to the Daemon. After repeated failures the error is propagated.
    """
    retries = 5
    last_error = None
    while retries > 0:
        try:
            return func(*args, **kwargs)
        except docker.errors.DockerException as e:
            # We shouldn't retry when the Docker API give errors
            raise e
        except (requests.exceptions.RequestException) as e:
            # On network issues we should retry
            logger.debug('Failed docker call %s: %s' % (func, e))
            last_error = e
            retries -= 1
        sleep(1)

    logger.error('Docker call %s failed after several tries: %s' % (func,
                                                                    last_error))
    raise last_error


def trym(func, *args, **kwargs):
    """
    Tries a mongo operation that might fail due to underlying issues in the
    connectetion to the database. After repeated failures the error is propagated.
    """
    retries = 5
    last_error = None
    while retries > 0:
        try:
            return func(*args, **kwargs)
        except (pymongo.errors.PyMongoError) as e:
            logger.debug('Failed mongo operation %s: %s' % (func, e))
            last_error = e
            retries -= 1
        sleep(1)

    logger.error('Mongo operation %s failed after several tries: %s' %
                 (func, last_error))
    raise last_error


def print_crash_analysis():
    print()
    print('========= Crash Analysis =========')
    print('Time: %s' % datetime.datetime.now())
    print('Last error: %s' % sys.exc_info()[0])
    print('Stack trace: \n%s' % traceback.print_exc())
    print('Cpu usage: %s' % psutil.cpu_percent(percpu=True))
    print('Memory usage:', psutil.virtual_memory())
    print()
