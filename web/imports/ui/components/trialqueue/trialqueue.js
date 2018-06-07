import { TrialQueue, TrialInsertSchema } from '/imports/api/trialqueue/trialqueue.js';
import { Meteor } from 'meteor/meteor';
import './trialqueue.html';

Template.trialqueue.helpers({
  trialqueue() {
    return TrialQueue.find({}, {sort: {start_time: -1}});
  },
  TrialInsertSchema() {
    return TrialInsertSchema;
  },
  TrialQueue() {
    return TrialQueue;
  },
});

AutoForm.hooks({
  insertTrial: {
    onSubmit: function (insertDoc, updateDoc, currentDoc) {
      this.event.preventDefault();

      let param_space = null;
      try {
        param_space = JSON.parse(insertDoc.param_space)
      } catch (e) {
        this.done(new Error("Parsing JSON failed"));
        return false;
      }

      doc = {
        data: {
          docker: {
            image: insertDoc.docker_image
          },
          volumes: {
            results: insertDoc.results_path,
            data: insertDoc.data_path,
          }
        },
        param_space: param_space
      }

      if (TrialQueue.insert(doc)) {
        this.done();
      } else {
        this.done(new Error("Submission failed"));
      }
      return false;
    }
  }
});
