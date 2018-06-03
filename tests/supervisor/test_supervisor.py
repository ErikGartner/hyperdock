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

from hyperdock.supervisor.supervisor import Supervisor
from hyperdock.common.experiment import MockExperiment
from hyperdock.common.workqueue import WorkQueue
from hyperdock.common.trialqueue import TrialQueue


class TestSupervisor(TestCase):

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.supervisor = Supervisor(self.db)

        collection = self.db.trialqueue
        # Default data
        collection.insert({
            'start_time': -1,
            'end_time': -1,
            'created_on': datetime.utcnow(),
            'priority': 1,
            'param_space': {
                'learning_rate': [0.1, 0.001],
                'solver': ['adam', 'adagrad'],
            },
        })

    def test_process_trials(self):
        collection = self.db.trialqueue
        self.assertEqual(collection.find({'start_time': -1}).count(), 1,
                         'Empty before start')

        self.supervisor._process_trials()
        self.assertEqual(collection.find({'start_time': -1}).count(), 0,
                         'Trials not dequeued before start')

        workq = self.db.workqueue
        self.assertEqual(workq.find({'start_time': -1}).count(), 4,
                         'Missing parameter combinations')
        self.assertEqual(workq.find({'payload':
                                     {'learning_rate': 0.001,
                                      'solver': 'adagrad'}
                                     }).count(), 1,
                         'Missing parameter combination')
