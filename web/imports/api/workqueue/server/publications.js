import { Meteor } from 'meteor/meteor';
import { WorkQueue } from '../workqueue.js';

Meteor.publish('workqueue.all', function () {
  return WorkQueue.find();
});
