import { Meteor } from 'meteor/meteor';
import { WorkQueue } from '../workqueue.js';

Meteor.publish('workqueue.all.limited', function () {
  return WorkQueue.find({}, { fields: { update: 0, parameters: 0 }});
});
