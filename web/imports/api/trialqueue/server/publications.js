import { Meteor } from 'meteor/meteor';
import { publishComposite } from 'meteor/reywood:publish-composite';

import { TrialQueue } from '../trialqueue.js';
import { WorkQueue } from '../../workqueue/workqueue.js';
import { Workers } from '/imports/api/workers/workers.js';

publishComposite('trialqueue.finished', function (limit) {
  return {
    find() {
      return TrialQueue.find({end_time: {$ne: -1}}, {sort: {end_time: -1}, limit: limit});
    },
    children: [{
      find(trial) {
        return WorkQueue.find({'trial': trial._id}, {fields: { update: 0, parameters: 0 }});
      }
    }]
  };
});

publishComposite('trialqueue.active', function () {
  return {
    find() {
      return TrialQueue.find({end_time: -1}, {sort: {start_time: 1}});
    },
    children: [{
      find(trial) {
        return WorkQueue.find({'trial': trial._id}, {fields: { update: 0, parameters: 0 }});
      }
    }]
  };
});

publishComposite('trial',  function (_id) {
  return {
    find() {
      return TrialQueue.find(_id);
    },
    children: [{
      find(trial) {
        return WorkQueue.find({'trial': trial._id});
      },
      children: [{
        find(work) {
          return Workers.find({id: work.id});
        }
      }]
    }]
  };
});
