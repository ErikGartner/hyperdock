import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { TrialQueue } from './trialqueue.js';
import { WorkQueue } from '../workqueue/workqueue.js';

Meteor.methods({
  'trialqueue.cancel'(id) {
    check(id, String);

    let t = TrialQueue.findOne({_id: id, end_time: -1});
    if (t == null) {
      throw new Meteor.Error('trialqueue.cancel called with invalid id.');
    }

    let end_time = new Date();
    TrialQueue.update(id, {$set: {end_time: end_time}});

    let works = WorkQueue.find({trial: id, end_time: -1, cancelled: false});
    works.forEach(function (w){
      w.cancelled = true;
      w.end_time = end_time;
      if (w.start_time == -1) {
        w.start_time = w.end_time;
      }
      WorkQueue.update(w._id, {$set: {cancelled: w.cancelled,
                                      end_time: w.end_time,
                                      start_time: w.start_time}});
    });

  }
});
