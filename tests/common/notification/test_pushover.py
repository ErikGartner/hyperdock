from unittest import TestCase, mock
import os

from hyperdock.common.notification.pushover import Pushover


class TestSlack(TestCase):
    def test_verify_credentials(self):
        """
        test verifing pushover credentials
        """
        self.assertFalse(
            Pushover.verify_credentials(), "Should return False when not configured"
        )

        os.environ["PUSHOVER_API_TOKEN"] = "INVALID"
        os.environ["PUSHOVER_USER_KEY"] = "INVALID"
        self.assertFalse(
            Pushover.verify_credentials(), "Should return False for invalid Token"
        )

    def test_send(self):
        """
        test sending slack message
        """
        os.environ["PUSHOVER_API_TOKEN"] = "T"
        os.environ["PUSHOVER_USER_KEY"] = "U"

        pushover = Pushover()

        # Assume incorrect Token/user_key
        pushover.client.send_message = mock.MagicMock(return_value=False)

        res = pushover.send("title", "msg")
        self.assertFalse(res, "Should be False on Pushover error")
        pushover.client.send_message.assert_called_with("msg", title="title")

        # Assume valid config
        pushover.client.send_message.return_value = True
        res = pushover.send("title", "msg")
        self.assertTrue(res, "Should not be False on success")
        pushover.client.send_message.assert_called_with("msg", title="title")
