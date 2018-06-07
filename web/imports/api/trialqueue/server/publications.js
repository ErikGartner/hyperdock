import { Meteor } from 'meteor/meteor';
import { publishComposite } from 'meteor/reywood:publish-composite';

import { TrialQueue } from '../trialqueue.js';
import { WorkQueue } from '../../workqueue/workqueue.js';

Meteor.publish('trialqueue.all', function () {
  return TrialQueue.find();
});

publishComposite('trial',  function (_id) {
  return {
    find() {
      return TrialQueue.find(_id);
    },
    children: [{
      find(trial) {
        return WorkQueue.find({'trial': trial._id});
      }
    }]
  };
});
