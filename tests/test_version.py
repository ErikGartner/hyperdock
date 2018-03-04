#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of hyperdock.
# http://github.com/ErikGartner/hyperdock

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2018, Erik Gärtner <erik@gartner.io>

from hyperdock import __version__
from tests.base import TestCase


class VersionTestCase(TestCase):
    def test_has_proper_version(self):
        self.assertEqual(__version__, '0.1.0')
