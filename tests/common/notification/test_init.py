from unittest import TestCase, mock
import os

from hyperdock.common.notification import valid_services
import hyperdock.common.notification


class TestNotiticationInit(TestCase):
    def tearDown(self):
        # Reset cached list of valid services
        hyperdock.common.notification._VALID_SERVICES = None

    def test_valid_services_empty_on_invalid(self):
        """
        test that valid_services returns empty list on invalid
        """
        self.assertListEqual(valid_services(), [])

    @mock.patch("hyperdock.common.notification.Pushover")
    def test_valid_services(self, mock_class):
        """
        test that valid_services returns valid services
        """
        mock_class.verify_credentials.return_value = True
        self.assertEqual(len(valid_services()), 1)
