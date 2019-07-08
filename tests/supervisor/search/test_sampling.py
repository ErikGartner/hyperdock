from unittest import TestCase, mock
import os

from hyperdock.supervisor.search.sampling import sample_values, get_distribution


class TestSearch(TestCase):
    def test_get_distribution(self):
        """test retrieving distribution by name"""
        self.assertIsNotNone(get_distribution("expon"))

    def test_sample_values(self):
        res = sample_values({"hdock_distr": "expon", "hdock_samples": 5})
        self.assertEqual(len(res), 5)

        res = sample_values({"hdock_distr": "expon"})
        self.assertEqual(res, None)
