import logging
import unicodedata
import re
import os

from .notification import Slack, Pushover, valid_services

logger = logging.getLogger("utils")


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
    return os.environ.get("HYPERDOCK_IN_DOCKER", "false").lower() == "true"


def setup_logging(level=logging.INFO):
    """
    Setups the format string and config for the Python logging module.
    """
    FORMAT = "[%(asctime)-15s - %(levelname)s - %(name)s in %(filename)s:%(lineno)s - %(funcName)s()]: %(message)s\n"
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(level)


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(value)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def send_notifiction(title, msg):
    """
    Send a notification to the preconfigured recipients.
    """
    services = valid_services()
    results = [s.send_message(title, msg) for s in services]
    return all(results)
