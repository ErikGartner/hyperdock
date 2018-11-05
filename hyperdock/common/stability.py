"""
The module contains functions used for stability and crash analysis.
"""
import logging
from time import sleep

import requests

logger = logging.getLogger('stability')


def tryd(func, *args, **kwargs):
    """
    Tries a Docker call that might fail due to underlying issues in the
    connectetion to the Daemon. After repeated failures the error is propagated.
    """
    retries = 10
    last_error = None
    while retries > 0:
        try:
            return func(*args, **kwargs)
        except (requests.exceptions.RequestException) as e:
            logger.debug('Failed docker call %s: %s' % (func, e))
            last_error = e
            retries -= 1
        sleep(0.5)

    logger.error('Docker call %s failed after several tries: %s' % (func,
                                                                    last_error))
    raise last_error
