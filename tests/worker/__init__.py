#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of hyperdock.
# http://github.com/ErikGartner/hyperdock

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2018, Erik Gärtner <erik@gartner.io>

from hyperdock.worker.worker import Worker
from tests.base import TestCase


class WorkerTestCase(TestCase):

    def test_simple_execute(self):
        self.assertEqual(__version__, '0.1.0')
