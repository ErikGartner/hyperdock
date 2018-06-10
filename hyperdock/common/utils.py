import logging


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
