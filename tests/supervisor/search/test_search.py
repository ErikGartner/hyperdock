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
        params = Search.expand({"a": 1})
        self.assertListEqual(params, [{"a": 1}])

        params = Search.expand([{"a": 1}, {"b": 2}])
        self.assertListEqual(params, [{"a": 1}, {"b": 2}])

    def test_grid_expand_spec(self):
        """
        test grid parameter spec expansion
        """
        params = Search._expand_spec({"a": [1, 2], "b": 1})
        self.assertListEqual(params, [{"a": 1, "b": 1}, {"a": 2, "b": 1}])

    def test_grid_expand_spec_with_sampling(self):
        """
        test grid parameter spec expansion with sampling
        """
        params = Search._expand_spec(
            {
                "a": [1, 2],
                "b": 1,
                "c": {
                    "hdock_distr": "expon",
                    "hdock_samples": 2,
                    "hdock_seed": 1,
                    "hdock_distr_kwargs": {"scale": 5},
                },
            }
        )
        expected = [
            {"a": 1, "b": 1, "c": 2.698029186295927},
            {"a": 1, "b": 1, "c": 6.370626265066521},
            {"a": 2, "b": 1, "c": 2.698029186295927},
            {"a": 2, "b": 1, "c": 6.370626265066521},
        ]
        self.assertListEqual(params, expected)
