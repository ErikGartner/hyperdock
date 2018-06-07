// Import needed templates

Router.configure({
  layoutTemplate: 'ApplicationLayout'
});

Router.route('/', {
  name: 'Home',
  subscriptions: function() {
   return [Meteor.subscribe('workers.all'),
           Meteor.subscribe('trialqueue.all'),
           Meteor.subscribe('workqueue.all')];
  }
});

Router.route('/trial/:trialId', {
  name: 'Trial',
  subscriptions: function() {
   return [Meteor.subscribe('trial', this.params.trialId)];
  }
});
