import { TrialQueue, TrialInsertSchema } from '/imports/api/trialqueue/trialqueue.js';
import { Meteor } from 'meteor/meteor';
import './trialqueue.html';

Template.trialqueue.helpers({
  trialqueue() {
    return TrialQueue.find({}, {sort: {start_time: -1}});
  },
  TrialInsertSchema() {
    return TrialInsertSchema;
  },
  TrialQueue() {
    return TrialQueue;
  },
});
