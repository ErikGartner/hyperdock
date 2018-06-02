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

from hyperdock.common.workqueue import WorkQueue


class TestWorkQueue(TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.q = WorkQueue(self.db)
        self.collection = self.db.workqueue

        # Default data
        self.payload = 'payload1'
        self.q.add_job(self.payload)

    def test_add_job(self):
        self.assertEqual(self.collection.count(), 1, 'Failed to add to queue')
        self.assertEqual(self.collection.find_one()['payload'], self.payload,
                         'Incorrect payload')
        self.assertAlmostEquals(self.collection.find_one()['created_on'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))
        self.assertEqual(self.collection.find_one()['start_time'],
                         -1, msg='Timestamp off',)
        self.assertEqual(self.collection.find_one()['end_time'],
                         -1, msg='Timestamp off',)
        self.assertEqual(self.collection.find_one()['last_update'],
                         -1, msg='Timestamp off',)

    def test_take_job(self):
        worker_id = 'worker1'
        job = self.q.assign_next_job(worker_id)

        self.assertEqual(job['payload'], self.payload)
        self.assertEqual(job['worker'], worker_id)
        self.assertAlmostEquals(job['start_time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))
        self.assertAlmostEquals(job['last_update'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))

        result = 'result1'
        self.q.finish_job(job['_id'], result)

        self.assertEqual(self.collection.find_one({'_id': job['_id']})['result'], result,
                         'Failed to add result')
        self.assertAlmostEquals(self.collection.find_one({'_id': job['_id']})['end_time'],
                                datetime.utcnow(), msg='Timestamp off',
                                delta=timedelta(seconds=5))