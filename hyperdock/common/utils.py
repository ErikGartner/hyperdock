

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
