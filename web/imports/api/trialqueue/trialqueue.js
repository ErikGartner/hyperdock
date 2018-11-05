import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import { check, Match } from 'meteor/check';

export const TrialQueue = new Mongo.Collection('trialqueue');

TrialSchema = new SimpleSchema({
  name: {
    label: 'Trial Name',
    type: String,
  },
  start_time: {
    type: SimpleSchema.oneOf(Date, SimpleSchema.Integer),
    autoValue: function() {
      if (this.isInsert) {
        return -1;
      }
    }
  },
  end_time: {
    type: SimpleSchema.oneOf(Date, SimpleSchema.Integer),
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
    defaultValue: 0,
  },
  param_space: {
    type: Object,
    blackbox: true
  },
  data: {
    type: Object,
    blackbox: true
  },
  retries: {
    type: SimpleSchema.Integer,
    defaultValue: 100,
    min: 0,
  }
});
TrialQueue.attachSchema(TrialSchema);
TrialQueue.permit(['insert', 'update']).allowInClientCode();

function param_space_validator() {
  check(this.value, String);
  try {
    let j = JSON.parse(this.value);
    check(j, Match.OneOf(Object, [Object]));
  } catch (e) {
    return 'bad_json';
  }
  return undefined;
}

export const TrialInsertSchema = new SimpleSchema({
  name: {
    label: 'Trial Name',
    type: String,
  },
  docker_image: {
    label: 'Docker Image',
    type: String,
  },
  docker_runtime: {
    label: 'Docker Runtime',
    type: String,
    optional: true,
    defaultValue: '',
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
    custom: param_space_validator,
  },
  docker_environment: {
    label: 'Docker Environment',
    type: Array,
    optional: true,
    minCount: 0,
  },
  'docker_environment.$': {
    type: String
  },
  retries: {
    type: SimpleSchema.Integer,
    defaultValue: 5,
    min: 0,
  },
  priority: {
    type: SimpleSchema.Integer,
    defaultValue: 0
  },
}, { check, tracker: Tracker});

TrialInsertSchema.messageBox.messages({
  en: {
      'bad_json': 'Invalid JSON!',
    },
});
