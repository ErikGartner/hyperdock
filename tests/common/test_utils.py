from unittest import TestCase
from datetime import datetime, timedelta

from hyperdock.common.utils import try_key, slugify


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
