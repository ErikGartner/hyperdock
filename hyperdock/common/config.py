import os
import copy
import logging

import yaml

DEFAULT_CONFIG = {"STABILITY": {"RETRY": {"SLEEP_TIME": 1, "RETRIES": 5}}}

CONFIG = None
logger = logging.getLogger("config")


def config(path="config.yml", force_reload=False):
    """
    Read the config for this module.
    Priority is env, config.yml then defaults.
    """

    global CONFIG, DEFAULT_CONFIG
    if CONFIG is not None and not force_reload:
        return CONFIG

    # 1. Defaults. All items should have keys here.
    config = copy.deepcopy(DEFAULT_CONFIG)

    # 2. Read from config.yml
    if os.path.exists(path):
        with open(path, mode="r") as data_file:
            try:
                config.update(yaml.load(data_file))
            except yaml.scanner.ScannerError as e:
                logger.warning("Invalid YAML config: %s" % e)

    # 3. Environment
    for key in config:
        val = os.getenv(key, None)
        if val is not None:
            config[key] = val

    CONFIG = config
    return CONFIG
