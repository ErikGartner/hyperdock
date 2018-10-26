import { WorkQueue } from '/imports/api/workqueue/workqueue.js';
import { TrialQueue } from '/imports/api/trialqueue/trialqueue.js';
import { Meteor } from 'meteor/meteor';

import './workqueue.html';
import './resultgraph.js';

Template.workqueue.helpers({
  workqueue() {
    return WorkQueue.find({}, {sort: {"result.loss": 1, end_time: -1, start_time: -1}});
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
  onlyVariableParams(object) {
    if (object == undefined) {
      return '';
    }

    let trial = TrialQueue.findOne(this.trial);
    if (trial == null) {
      return null;
    }

    let params = [];
    _.keys(trial.param_space).forEach(function (key){
      let value = trial.param_space[key];
      if (_.isArray(value)) {
        params.push(key);
      }
    });
    let variable =  _.pick(object, params);
    return JSON.stringify(variable, null, '  ');
  },
  resultSummary() {
    if (this.result.state == null) {
      return 'N/A';
    } else if (this.result.state == 'ok') {
      return this.result.loss;
    } else if (this.result.state =='fail' && this.result.msg != null) {
      return this.result.msg;
    } else {
      return this.result.state;
    }
  },
});

Template.workqueue.events({
  'click .cancel-work': function (event) {
    let id = $(event.currentTarget).data().id;

    Meteor.call('workqueue.cancel', id, (error) => {
      if (error) {
        alert(error.error);
      }
    });
  }
})
