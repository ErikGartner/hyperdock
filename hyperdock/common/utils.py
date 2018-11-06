import logging
import unicodedata
import re
import os

import requests
import pushover
from slackclient import SlackClient

logger = logging.getLogger('utils')


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


def in_docker():
    """
    Checks if Hyperdock is running in its Docker image.
    """
    return os.environ.get('HYPERDOCK_IN_DOCKER', 'false').lower() == 'true'


def setup_logging(level=logging.INFO):
    """
    Setups the format string and config for the Python logging module.
    """
    FORMAT = '[%(asctime)-15s - %(levelname)s - %(name)s in %(filename)s:%(lineno)s - %(funcName)s()]: %(message)s\n'
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
    no_errors = True
    pushover_token = os.environ.get('PUSHOVER_API_TOKEN', None)
    pushover_user_key = os.environ.get('PUSHOVER_USER_KEY', None)
    if pushover_token is not None and pushover_user_key is not None:
        try:
            client = pushover.Client(pushover_user_key, api_token=pushover_token)
            client.send_message(msg, title=title)
        except (pushover.InitError, pushover.RequestError, pushover.UserError) as e:
            logger.error('Failed to send Pushover notification: %s' % e)
            no_errors = False

    slack_token = os.environ.get('SLACK_API_TOKEN', None)
    slack_recipient = os.environ.get('SLACK_RECIPIENT', None)
    if slack_recipient is not None and slack_token is not None:
        sc = SlackClient(slack_token)
        res = sc.api_call(
          'chat.postMessage',
          channel=slack_recipient,
          text='*%s:* %s' % (title, msg)
        )
        if not res['ok']:
            no_errors = False
            logger.error('Failed to send Slack notification: %s' % res)

    return no_errors
