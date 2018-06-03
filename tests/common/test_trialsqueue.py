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

from hyperdock.common.trialqueue import TrialQueue


class TestTrialQueue(TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.q = TrialQueue(self.db)
        self.collection = self.db.trialqueue

        # Default data
        self.collection.insert({
            'start_time': -1,
            'end_time': -1,
            'created_on': datetime.utcnow(),
            'priority': 1,
            'param_space': {
                'learning_rate': [0.1, 0.001],
                'solver': ['adam', 'adagrad'],
            },
        })

    def test_next_trial(self):
        self.assertEqual(self.collection.find({'start_time': -1}).count(), 1)
        trial = self.q.next_trial()
        self.assertEqual(self.collection.find({'start_time': -1}).count(), 0,
                         'Work not dequeued.')
        self.assertEqual(self.q.next_trial(), None, 'Work queue not empty')
