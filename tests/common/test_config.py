from unittest import TestCase, mock
import os

from hyperdock.common.config import config, DEFAULT_CONFIG
import hyperdock.common.config


import yaml


class TestConfig(TestCase):
    def tearDown(self):
        for key in DEFAULT_CONFIG:
            if key in os.environ:
                del os.environ[key]

    def test_default_exists(self):
        """
        config should contain defaults
        """
        self.assertDictEqual(config(force_reload=True), DEFAULT_CONFIG)

    def test_environment(self):
        """
        environment should overwrite config
        """
        cfg = {}
        for key in DEFAULT_CONFIG:
            cfg[key] = "test"
            os.environ[key] = "test"
        self.assertDictEqual(config(force_reload=True), cfg)

    def test_read_invalid_yaml(self):
        """
        invalid yaml should be skipped silently
        """
        self.assertDictEqual(config("LICENSE", force_reload=True), DEFAULT_CONFIG)

    def test_read_yaml(self):
        """
        invalid yaml should be skipped silently
        """
        cfg = {}
        cfg.update(DEFAULT_CONFIG)
        with open(".travis.yml", mode="r") as data_file:
            cfg.update(yaml.load(data_file))
        self.assertDictEqual(config(".travis.yml", force_reload=True), cfg)
