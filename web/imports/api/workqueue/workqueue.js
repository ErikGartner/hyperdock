import { Mongo } from 'meteor/mongo';

export const WorkQueue = new Mongo.Collection('workqueue');
