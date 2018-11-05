import { TrialQueue, TrialInsertSchema } from '/imports/api/trialqueue/trialqueue.js';
import { WorkQueue } from '../../../api/workqueue/workqueue.js';
import { Meteor } from 'meteor/meteor';
import './trialqueue.html';

Template.trialqueue.helpers({
  trialProgress(id) {
    let all = WorkQueue.find({trial: id, cancelled: false}).count();
    if (all < 1) {
      return 100;
    }
    let notDone = WorkQueue.find({trial: id, end_time: -1, cancelled: false}).count();
    return 100 * (1.0 - notDone / all);
  },
  trialqueue() {
    return TrialQueue.find({end_time: -1},
                           {sort: {start_time: -1}});
  },
  trialhistory() {
    return TrialQueue.find({end_time: {$ne: -1}},
                           {sort: {end_time: -1}});
  },
  TrialInsertSchema() {
    return TrialInsertSchema;
  },
  TrialQueue() {
    return TrialQueue;
  },
  prefilledTrial() {
    return Router.current().params.query;
  },
  trialLowestLoss() {
    let losses = WorkQueue.find({trial: this._id, 'result.state': 'ok'}).map((job) => {
      return job.result.loss;
    })
    losses = _.filter(losses, (loss) => {
      return !isNaN(loss);
    });
    if (losses.length > 0) {
      return _.min(losses);
    } else {
      return 'N/A';
    }
  },
  trialStats() {
    let activeTrials = TrialQueue.find({end_time: -1}, {sort: {start_time: -1}});
    let nbrTrials = activeTrials.count();

    let nbrQueuedJobs = _.reduce(activeTrials.map(function (doc) {
      let jobs = WorkQueue.find({trial: doc._id, end_time: -1});
      return jobs.count();
    }), function (a, b) { return a + b;}, 0);

    return {nbrTrials: nbrTrials, nbrQueuedJobs: nbrQueuedJobs};
  }
});

Template.trialqueue.events({
  'click .delete-trial': function (event) {
    let id = $(event.currentTarget).data().id;

    Meteor.call('trialqueue.delete', id, (error) => {
      if (error) {
        alert(error.error);
      }
    });
  }
})
