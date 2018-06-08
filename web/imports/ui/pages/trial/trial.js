import './trial.html';
import '../../components/workqueue/workqueue.js';
import { WorkQueue } from '../../../api/workqueue/workqueue.js';

Template.Trial.helpers({
  progress() {
    let not_done = WorkQueue.find({trial: this._id, end_time: -1}).count();
    let all = WorkQueue.find({trial: this._id}).count();
    return 100 * (1.0 - not_done / all);
  },
  notDone() {
    return this.end_time == -1;
  }
});

Template.Trial.events({
  'click .cancel-trial': function (event) {
    let id = $(event.target).data().id;

    Meteor.call('trialqueue.cancel', id, (error) => {
      if (error) {
        alert(error.error);
      }
    });
  }
})
