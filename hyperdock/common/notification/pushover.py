import os
import logging

import pushover

from .service import Service

logger = logging.getLogger("Pushover")


class Pushover(Service):
    def __init__(self):
        """
        Creates the slack object
        """
        self.token = os.environ.get("PUSHOVER_API_TOKEN", None)
        self.user_key = os.environ.get("PUSHOVER_USER_KEY", None)
        self.client = pushover.Client(self.user_key, api_token=self.token)

    @staticmethod
    def verify_credentials():
        """
        Checks if the service is properly set-up
        Returns True or False
        """
        token = os.environ.get("PUSHOVER_API_TOKEN", None)
        user_key = os.environ.get("PUSHOVER_USER_KEY", None)
        if token is None or user_key is None:
            return False

        client = pushover.Client(token, api_token=user_key)
        try:
            res = client.verify(user_key)
            ok = res is not None and res is not False
            if not ok:
                logger.warning("Credentials are invalid.")
            return ok
        except:
            return False

    def send(self, title, msg):
        """
        Send a message. Returns False on error else True
        """
        try:
            res = self.client.send_message(msg, title=title)
            return res is not None and res is not False
        except (pushover.InitError, pushover.RequestError, pushover.UserError) as e:
            logger.error("Failed to send Pushover notification: %s" % e)
            return False
