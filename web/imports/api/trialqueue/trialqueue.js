import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';

export const TrialQueue = new Mongo.Collection('trialqueue');

TrialSchema = new SimpleSchema({
    start_time: {
      type: SimpleSchema.Integer,
      autoValue: function() {
        if (this.isInsert) {
          return -1;
        }
      }
    },
    end_time: {
      type: SimpleSchema.Integer,
      autoValue: function() {
        if (this.isInsert) {
          return -1;
        }
      }
    },
    created_on: {
      type: Date,
      autoValue: function() {
        if (this.isInsert) {
          return new Date();
        } else {
          this.unset();  // Prevent user from supplying their own value
        }
      }
    },
    priority: {
      type: SimpleSchema.Integer,
      defaultValue: -1
    },
    param_space: {
      type: Object,
      blackbox: true
    },
    data: {
      type: Object,
      blackbox: true
    }
});
TrialQueue.attachSchema(TrialSchema);

TrialQueue.permit(['insert', 'update', 'remove']).allowInClientCode();

export const TrialInsertSchema = new SimpleSchema({
  docker_image: {
    label: 'Docker Image',
    type: String,
  },
  results_path: {
    type: String,
    label: 'Results Directory',
  },
  data_path: {
    type: String,
    label: 'Data Directory',
  },
  param_space: {
    label: 'Parameter Space',
    type: String,
  }
});
