import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { TrialQueue, TrialInsertSchema } from './trialqueue.js';
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

  },
  'trialqueue.insert'(insertDoc) {

    TrialInsertSchema.clean(insertDoc);
    TrialInsertSchema.validate(insertDoc);

    let param_space = null;
    try {
      param_space = JSON.parse(insertDoc.param_space)
    } catch (e) {
      throw new Meteor.Error(e);
    }

    doc = {
      name: insertDoc.name,
      data: {
        docker: {
          image: insertDoc.docker_image,
          runtime: insertDoc.docker_runtime,
          environment: insertDoc.docker_environment,
        },
        volumes: {
          results: insertDoc.results_path,
          data: insertDoc.data_path,
        }
      },
      param_space: param_space,
      retries: insertDoc.retries,
      priority: insertDoc.priority,
    }

    return TrialQueue.insert(doc);
  },

  'trialqueue.delete'(id) {
    check(id, String);

    let t = TrialQueue.findOne({_id: id, end_time: {$ne: -1}});
    if (t == null) {
      throw new Meteor.Error('trialqueue.delete called with invalid id.');
    }

    if (Meteor.isServer) {
      WorkQueue.remove({trial: id});
      return TrialQueue.remove({_id: id}) > 0;
    }
  }
});
