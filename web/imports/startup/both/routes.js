import { Tracker } from 'meteor/tracker'

import { TrialQueue } from '../../api/trialqueue/trialqueue.js';
import { WorkQueue } from '../../api/workqueue/workqueue.js';

Router.configure({
  layoutTemplate: 'ApplicationLayout'
});

Router.route('/', {
  name: 'Home',
  subscriptions: function() {
    Session.set('nbr-finished-trials', 10);
    Tracker.autorun(() => {
      Meteor.subscribe('workers.all'),
      Meteor.subscribe('trialqueue.finished', Session.get('nbr-finished-trials')),
      Meteor.subscribe('trialqueue.active')
    });
  }
});

Router.route('/trial/:trialId', {
  name: 'Trial',
  subscriptions: function() {
   return [Meteor.subscribe('trial', this.params.trialId)];
  },
  data: function() {
    return TrialQueue.findOne(this.params.trialId);
  }
});

Router.route('/job/:jobId', function () {
  job = WorkQueue.findOne(this.params.jobId);
  if (job) {
    var redirectUrl = '/trial/' + job.trial;
  } else {
    var redirectUrl = '/';
  }

  this.response.writeHead(302, {
    'Location': redirectUrl
  });
  this.response.end();
}, {where: 'server'});
