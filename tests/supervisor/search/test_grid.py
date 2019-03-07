from unittest import TestCase, mock
import os

from hyperdock.supervisor.search.grid import Grid


class TestSearch(TestCase):
    def test_expand_spec(self):
        """
        test grid parameter spec expansion
        """
        params = Grid._expand_spec({"a": [1, 2], "b": 1})
        self.assertListEqual(params, [{"a": 1, "b": 1}, {"a": 2, "b": 1}])
