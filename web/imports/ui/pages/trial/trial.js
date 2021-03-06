import { _ } from 'lodash';

import './trial.html';
import '../../components/workqueue/workqueue.js';
import { WorkQueue } from '../../../api/workqueue/workqueue.js';
import { TrialQueue } from '../../../api/trialqueue/trialqueue.js';

Template.Trial.helpers({
  progress() {
    let all = WorkQueue.find({trial: this._id, cancelled: false}).count();
    if (all < 1) {
      return 0;
    }
    let notDone = WorkQueue.find({trial: this._id, end_time: -1, cancelled: false}).count();
    return 100 * (1.0 - notDone / all);
  },
  notDone() {
    return this.end_time == -1;
  }
});

Template.Trial.events({
  'click .cancel-trial': function (event) {
    let id = $(event.currentTarget).data().id;

    Meteor.call('trialqueue.cancel', id, (error) => {
      if (error) {
        alert(error.error);
      }
    });
  },
  'click .clone-trial': function (event) {
    let id = $(event.currentTarget).data().id;
    let t = TrialQueue.findOne(id);
    if (t == undefined) {
      alert('Invalid trial id!');
      return;
    }

    let trial_spec = {
      name: t.name,
      docker_image: t.data.docker.image,
      docker_runtime: _.defaultTo(t.data.docker.runtime, ''),
      results_path: t.data.volumes.results,
      data_path: t.data.volumes.data,
      docker_environment: t.data.docker.environment,
      param_space: JSON.stringify(t.param_space, null, '  '),
      priority: t.priority,
      retries: 100, // We set it to 100 since we don't know original value.
    };

    Router.go('Home', {}, {query: trial_spec});
  },
})
