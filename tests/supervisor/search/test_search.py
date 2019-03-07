from unittest import TestCase, mock
import os

from hyperdock.supervisor.search.search import Search


class TestSearch(TestCase):
    def test_list_wrap(self):
        """
        test list wrapping function
        """
        a = dict(a=1, b=[1, 2])
        a_wrap = Search.list_wrap(a)
        self.assertListEqual(a_wrap, [a], "Should be wrapped in list")

        a_wrap_2 = Search.list_wrap(a_wrap)
        self.assertListEqual(a_wrap_2, a_wrap, "Should not double wrap in list")

    def test_expand(self):
        """
        test the parameter expansion loop
        It takes one or more parameters specs and returns a list of
        combinations to try.
        """
        Search._expand_spec = mock.MagicMock(return_value=[1])
        params = Search.expand({"a": 1}, extra_config=2)
        self.assertListEqual(params, [1])
        Search._expand_spec.assert_called_with({"a": 1}, extra_config=2)

        params = Search.expand([{"a": 1}, {"b": 2}])
        self.assertListEqual(params, [1, 1])
