import { WorkQueue } from '/imports/api/workqueue/workqueue.js';
import { Meteor } from 'meteor/meteor';
import './workqueue.html';

Template.workqueue.helpers({
  workqueue() {
    return WorkQueue.find({}, {sort: {start_time: 1}});
  },
  rowColor() {
    let w = WorkQueue.findOne(this._id);
    if (w == null) {
      return '';
    } else if (w.cancelled) {
      return 'warning';
    } else if (w.start_time != -1 && w.end_time == -1) {
      return 'info';
    } else if (w.end_time != -1 && w.result.state == 'ok') {
      return 'success';
    } else if (w.end_time != -1 && w.result.state == 'fail') {
      return 'danger';
    }
    return '';
  },
  notCancellable() {
    let w = WorkQueue.findOne(this._id);
    return (w.cancelled || w.end_time != -1);
  },
});

Template.workqueue.events({
  'click .cancel-work': function (event) {
    let id = $(event.target).data().id;

    Meteor.call('workqueue.cancel', id, (error) => {
      if (error) {
        alert(error.error);
      }
    });
  }
})
