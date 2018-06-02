#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of hyperdock.
# http://github.com/ErikGartner/hyperdock

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2018, Erik Gärtner <erik@gartner.io>

from unittest import TestCase
from datetime import datetime, timedelta

import mongomock

from hyperdock.worker.worker import Worker


class TestWorker(TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.worker = Worker({}, self.db)

    def test_register_worker(self):
        collection = self.db.workers
        self.assertEqual(collection.count(), 0, 'Not empty before start')

        self.worker._register_worker()
        self.assertEqual(collection.count(), 1, 'Failed to register worker')

        self.assertEqual(collection.find_one()['id'], self.worker.id, 'Incorrect id')
        self.assertAlmostEquals(collection.find_one()['time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))
