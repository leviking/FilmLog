// Shared Functions for other JavaScript files
/* eslint no-unused-vars: 0 */

// Show an alert within an alert div tag
// (to be placed on the HTML page)
function showAlert(strong, message, color) {
  const body = `<div class="alert alert-${color} alert-fixed alert-dismissible fade show" role="alert" id="test"> \
      <strong>${strong}</strong> ${message} \
      <button type="button" class="close" data-dismiss="alert" aria-label="Close"> \
        <span aria-hidden="true">&times;</span> \
      </button> \
    </div>`;
  $('#alert').html(body);
  $('#alert').delay(2000).fadeOut(2000);
  $('#alert').show();
}
