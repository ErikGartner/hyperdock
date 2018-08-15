import { TrialQueue, TrialInsertSchema } from '/imports/api/trialqueue/trialqueue.js';
import { WorkQueue } from '../../../api/workqueue/workqueue.js';
import { Meteor } from 'meteor/meteor';
import './trialqueue.html';

Template.trialqueue.helpers({
  trialProgress(id) {
    let not_done = WorkQueue.find({trial: id, end_time: -1}).count();
    let all = WorkQueue.find({trial: id}).count();
    return 100 * (1.0 - not_done / all);
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
});

Template.trialqueue.events({
  'click .delete-trial': function (event) {
    let id = $(event.target).data().id;
    console.log(event);

    Meteor.call('trialqueue.delete', id, (error) => {
      if (error) {
        alert(error.error);
      }
    });
  }
})
