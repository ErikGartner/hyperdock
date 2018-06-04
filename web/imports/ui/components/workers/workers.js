import { Workers } from '/imports/api/workers/workers.js';
import { Meteor } from 'meteor/meteor';
import './workers.html';

Template.workers.helpers({
  workers() {
    return Workers.find({});
  },
});
