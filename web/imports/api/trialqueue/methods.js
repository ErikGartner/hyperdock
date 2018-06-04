
import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { TrialQueue } from './trialqueue.js';

Meteor.methods({
  'trialqueue.insert'(docker_image, param_space) {
    check(docker_image, String);
    check(param_space, String);

    let p = JSON.parse(param_space);

    return TrialQueue.insert({
      docker_image: docker_image,
      param_space: p,
      created_on: new Date(),
      start_time: -1,
      end_time: -1,
      priority: 1
    });
  },
});
