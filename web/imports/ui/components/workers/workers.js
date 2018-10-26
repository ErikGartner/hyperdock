import { Workers } from '/imports/api/workers/workers.js';
import { Meteor } from 'meteor/meteor';
import './workers.html';

Template.workers.helpers({
  workers() {
    return Workers.find({});
  },
  nbrJobs() {
    return this.jobs.length;
  },
  totalParallelism() {
    let parallelism = Workers.find({}).map(function(w) {return w.parallelism;});
    return _.reduce(parallelism, function(a, b) {return a+b;}, 0);
    //_.reduce();
  },
  totalLoad() {
    let load = Workers.find({}).map(function(w) {return w.jobs.length;});
    return _.reduce(load, function(a, b) {return a+b;}, 0);
  }
});
