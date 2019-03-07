from unittest import TestCase, mock
import os

from hyperdock.common.notification.slack import Slack


class TestSlack(TestCase):
    @mock.patch("hyperdock.common.notification.slack.SlackClient.api_call")
    def test_verify_credentials(self, mock_func):
        """
        test verifing slack credentials
        """
        mock_func.return_value = {"ok": False}

        self.assertFalse(
            Slack.verify_credentials(), "Should return False when not configured"
        )

        os.environ["SLACK_API_TOKEN"] = "INVALID"
        os.environ["SLACK_RECIPIENT"] = "INVALID"
        self.assertFalse(
            Slack.verify_credentials(), "Should return False for invalid Token"
        )

        os.environ["SLACK_API_TOKEN"] = "VALID"
        os.environ["SLACK_RECIPIENT"] = "VALID"

        mock_func.return_value = {"ok": True}
        self.assertTrue(
            Slack.verify_credentials(), "Should return False for invalid Token"
        )

    @mock.patch("hyperdock.common.notification.slack.SlackClient.api_call")
    def test_send(self, mock_func):
        """
        test sending slack message
        """
        os.environ["SLACK_API_TOKEN"] = "T"
        os.environ["SLACK_RECIPIENT"] = "R"

        # Assume invalid config
        mock_func.return_value = {"ok": False}

        slack = Slack()

        res = slack.send("title", "msg")
        self.assertFalse(res, "Should be False on Slack error")
        mock_func.assert_called_with(
            "chat.postMessage", channel="R", text="*{}:* {}".format("title", "msg")
        )

        # Assume valid config
        mock_func.return_value = {"ok": True}

        res = slack.send("title", "msg")
        self.assertTrue(res, "Should be True on ok status")
        mock_func.assert_called_with(
            "chat.postMessage", channel="R", text="*{}:* {}".format("title", "msg")
        )
