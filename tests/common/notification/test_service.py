from unittest import TestCase, mock
import os

from hyperdock.common.notification.service import Service


class TestSlack(TestCase):
    def test_verify_credentials(self):
        """
        Service should raise NotImplementedError for verify_credentials
        """
        with self.assertRaises(NotImplementedError):
            Service.verify_credentials()

    def test_send(self):
        """
        Service should raise NotImplementedError for send
        """
        with self.assertRaises(NotImplementedError):
            Service.verify_credentials()
