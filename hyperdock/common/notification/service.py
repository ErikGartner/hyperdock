class Service:
    def __init__(self):
        """
        Creates the service object
        """
        pass

    @staticmethod
    def verify_credentials():
        """
        Checks if the service is properly set-up
        Returns True or False
        """
        raise NotImplementedError

    def send(self, title, msg):
        """
        Send a message. Returns False on error else True
        """
        raise NotImplementedError
