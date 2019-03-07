import os
import logging

from slackclient import SlackClient

from .service import Service

logger = logging.getLogger("Slack")


class Slack(Service):
    def __init__(self):
        """
        Creates the slack object
        """
        self.token = os.environ.get("SLACK_API_TOKEN", None)
        self.recipient = os.environ.get("SLACK_RECIPIENT", None)
        self.client = SlackClient(self.token)

    @staticmethod
    def verify_credentials():
        """
        Checks if the service is properly set-up
        Returns True or False
        """
        token = os.environ.get("SLACK_API_TOKEN", None)
        recipient = os.environ.get("SLACK_RECIPIENT", None)
        if recipient is None or token is None:
            return False

        sc = SlackClient(token)
        ok = sc.api_call("channels.list")["ok"]
        if not ok:
            logger.warning("Credentials are invalid.")
        return ok

    def send(self, title, msg):
        """
        Send a message. Returns False on error else True
        """
        res = self.client.api_call(
            "chat.postMessage",
            channel=self.recipient,
            text="*{}:* {}".format(title, msg),
        )
        return res["ok"]
