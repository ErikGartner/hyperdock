import { Meteor } from 'meteor/meteor';
import { TrialQueue } from '../trialqueue.js';

Meteor.publish('trialqueue.all', function () {
  return TrialQueue.find();
});
