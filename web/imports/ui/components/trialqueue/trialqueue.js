import { TrialQueue } from '/imports/api/trialqueue/trialqueue.js';
import { Meteor } from 'meteor/meteor';
import './trialqueue.html';

Template.trialqueue.helpers({
  trialqueue() {
    return TrialQueue.find({});
  },
});
