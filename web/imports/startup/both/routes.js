import { TrialQueue } from '../../api/trialqueue/trialqueue.js';


Router.configure({
  layoutTemplate: 'ApplicationLayout'
});

Router.route('/', {
  name: 'Home',
  subscriptions: function() {
    return [Meteor.subscribe('workers.all'),
            Meteor.subscribe('trialqueue.finished', 10),
            Meteor.subscribe('trialqueue.active')];
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
