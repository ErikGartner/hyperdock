import { WorkQueue } from '/imports/api/workqueue/workqueue.js';
import { Meteor } from 'meteor/meteor';
import './workqueue.html';

Template.workqueue.helpers({
  workqueue() {
    return WorkQueue.find({});
  },
});
