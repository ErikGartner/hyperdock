import { TrialQueue } from '/imports/api/trialqueue/trialqueue.js';
import { Meteor } from 'meteor/meteor';
import './trialqueue.html';

Template.trialqueue.helpers({
  trialqueue() {
    return TrialQueue.find({});
  },
});

Template.trialqueue.events({
  'submit .add-trial'(event) {
    event.preventDefault();

    const target = event.target;
    const docker_image = target.docker_image;
    const param_space = target.param_space;

    Meteor.call('trialqueue.insert', docker_image.value, param_space.value, (error) => {
      if (error) {
        alert(error.error);
      } else {
        docker_image.value = '';
        param_space.value = '';
      }
    });
  },
});
