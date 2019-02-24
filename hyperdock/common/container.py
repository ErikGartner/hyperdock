


class Container():
    """
    A wrapper class for the Docker container.
    Performs error checking and stability checks.
    """

    def __init__(image, env, privileged=False):
