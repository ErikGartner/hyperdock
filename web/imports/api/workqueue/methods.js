import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { WorkQueue } from './workqueue.js';

Meteor.methods({
  'workqueue.cancel'(id) {
    check(id, String);

    let w = WorkQueue.findOne({_id: id, end_time: -1, cancelled: false});
    if (w == null) {
      throw new Meteor.Error('workqueue.cancel called with invalid id.');
    }

    let update = {
      cancelled: true,
      end_time: new Date(),
    }

    if (w.start_time == -1) {
      update.start_time = update.end_time;
    }

    return WorkQueue.update({_id: id}, {$set: update});
  }
});
