// Import client startup through a single index entry
import './global_helpers.js';
import '../../ui';

AutoForm.hooks({
  insertTrial: {
    onSuccess: function(formType, result) {
      // On a successful submission, we clear the IronRouter query params.
      Router.go('Home');
    }
  }
});
