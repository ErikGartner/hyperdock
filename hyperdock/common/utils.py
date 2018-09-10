import logging
import unicodedata
import re
import os

import pushover


def try_key(dictionary, default, *keys):
    """
    Tries to get all keys in a nested dictionary.
    """
    try:
        res = dictionary
        for k in keys:
            res = res[k]
        return res
    except (KeyError, IndexError) as e:
        return default


def setup_logging(level=logging.DEBUG):
    """
    Setups the format string and config for the Python logging module.
    """
    FORMAT = '%(asctime)-15s - %(name)-25s - %(levelname)s - %(threadName)s - %(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(level)


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def send_notifiction(title, msg):
    """
    Send a notification to the preconfigured recipients.
    """
    pushover_token = os.environ.get('PUSHOVER_API_TOKEN', None)
    pushover_user_key = os.environ.get('PUSHOVER_USER_KEY', None)
    if pushover_token is not None and pushover_user_key is not None:
        try:
            client = pushover.Client(pushover_user_key, api_token=pushover_token)
            client.send_message(msg, title=title)
        except (pushover.InitError, pushover.RequestError, pushover.UserError) as e:
            log = logging.getLogger('utils.send_notifiction')
            log.error('Failed to send Pushover notification: %s' % e)
            return False

    return True
