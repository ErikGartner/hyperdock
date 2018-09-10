from unittest import TestCase
from datetime import datetime, timedelta
import os

from hyperdock.common.utils import try_key, slugify, send_notifiction


class TestUtils(TestCase):

    def test_try_key(self):
        d = {
            'a': {'b': [4]}
        }
        self.assertEqual(try_key(d, None, 'a', 'b'), [4], 'Should find array')
        self.assertEqual(try_key(d, None, 'a', 'b', 0), 4, 'Should enter array')
        self.assertEqual(try_key(d, None, 'a', 'c', 0), None, 'Should return default')
        self.assertEqual(try_key({}, None, 'a', 'c', 0), None, 'Should return default')
        self.assertEqual(try_key(d, None), d, 'Should return dict')

    def test_slugify(self):
        bad_str = 'this is a / bad . _ å ä ö é folder \ name'
        good_str = 'this-is-a-bad-_-a-a-o-e-folder-name'
        res = slugify(bad_str)
        self.assertEqual(res, good_str, 'Bad slugified string')

    def test_notification(self):
        self.assertTrue(send_notifiction('TEST', 'TEST'), 'Should return true when Pushover not configured.')

        os.environ['PUSHOVER_API_TOKEN'] = 'INVALID'
        os.environ['PUSHOVER_USER_KEY'] = 'INVALID'
        self.assertFalse(send_notifiction('TEST', 'TEST'), 'Should return false when Pushover is incorrectly configured.')

        del os.environ['PUSHOVER_API_TOKEN']
        del os.environ['PUSHOVER_USER_KEY']

        os.environ['SLACK_API_TOKEN'] = 'INVALID'
        os.environ['SLACK_RECIPIENT'] = 'INVALID'
        self.assertFalse(send_notifiction('TEST', 'TEST'), 'Should return false when Pushover is incorrectly configured.')
