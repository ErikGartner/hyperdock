// Import modules used by both client and server through a single index entry point
// e.g. useraccounts configuration file.
import SimpleSchema from 'simpl-schema';
import './routes.js';

SimpleSchema.extendOptions(['autoform']);
