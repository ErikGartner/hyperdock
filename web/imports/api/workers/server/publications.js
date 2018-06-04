import { Meteor } from 'meteor/meteor';
import { Workers } from '../workers.js';

Meteor.publish('workers.all', function () {
  return Workers.find();
});
