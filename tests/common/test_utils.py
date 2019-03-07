from unittest import TestCase
from datetime import datetime, timedelta
import os

import docker

from ..hyperdock_basetest import HyperdockBaseTest
from hyperdock.common.utils import *


class TestUtils(HyperdockBaseTest):
    def test_try_key(self):
        """
        try key should return value from (nested) dictionary if exists
        else it should return None
        """
        d = {"a": {"b": [4]}}
        self.assertEqual(try_key(d, None, "a", "b"), [4], "Should find array")
        self.assertEqual(try_key(d, None, "a", "b", 0), 4, "Should enter array")
        self.assertEqual(try_key(d, None, "a", "c", 0), None, "Should return default")
        self.assertEqual(try_key({}, None, "a", "c", 0), None, "Should return default")
        self.assertEqual(try_key(d, None), d, "Should return dict")

    def test_slugify(self):
        """
        slugify should make unsafe strings safe for paths
        """
        bad_str = "this is a / bad . _ å ä ö é folder \ name"
        good_str = "this-is-a-bad-_-a-a-o-e-folder-name"
        res = slugify(bad_str)
        self.assertEqual(res, good_str, "Bad slugified string")

    def test_notification(self):
        """
        send_notifiction should send notification is properly configured
        else it should fail silently and return False. Not that
        it should only return False on errors for a properly configured
        client.
        """
        self.assertTrue(
            send_notifiction("TEST", "TEST"),
            "Should return True when Pushover not configured.",
        )

        os.environ["PUSHOVER_API_TOKEN"] = "INVALID"
        os.environ["PUSHOVER_USER_KEY"] = "INVALID"
        self.assertTrue(
            send_notifiction("TEST", "TEST"),
            "Should return True when Pushover is incorrectly configured.",
        )

        del os.environ["PUSHOVER_API_TOKEN"]
        del os.environ["PUSHOVER_USER_KEY"]

        os.environ["SLACK_API_TOKEN"] = "INVALID"
        os.environ["SLACK_RECIPIENT"] = "INVALID"
        self.assertTrue(
            send_notifiction("TEST", "TEST"),
            "Should return True when Pushover is incorrectly configured.",
        )

    def test_setup_logging(self):
        """
        setup_logging should set logging level
        """
        import logging

        setup_logging(logging.CRITICAL)

        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.CRITICAL, "Incorrect logging level")
