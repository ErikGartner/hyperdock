import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';

import './methods.js';

export const WorkQueue = new Mongo.Collection('workqueue');

WorkSchema = new SimpleSchema({
  start_time: {
    type: Date,
    autoValue: function() {
      if (this.isInsert) {
        return -1;
      }
    }
  },
  end_time: {
    type: Date,
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
  parameters: {
    type: Object,
    blackbox: true
  },
  result: {
    type: Object,
    blackbox: true
  },
  worker: {
    type: String,
  },
  trial: {
    type: String,
  },
  cancelled: {
    type: Boolean,
  }
});
WorkQueue.attachSchema(WorkSchema);

WorkQueue.permit(['update']);
