// Shared Functions for other JavaScript files
/* eslint no-unused-vars: 0 */

// Shared Gets
// Get Project
function getProject(binderID, projectID) {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/binders/${binderID}/projects/${projectID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $('#projectName').html(data.data.name);
    },
  });
}

// Get Film Options
function getFilmOptions(films) {
  jQuery(films).each((i, film) => {
    $('#filmSizeID').append($(`<option value="${film.id}">${film.size}</option>`));
  });
}

// Get Film Sizes
function getFilmSizes() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/filmsizes',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      getFilmOptions(data.data);
    },
  });
}

// Get Film Types
// Make a call to pull the film types (e.g. Kodak Portra 400)
function getFilmTypes() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/films',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $('#filmTypeID').append($('<option value="0">None</option>'));
      jQuery(data.data).each((i, film) => {
        $('#filmTypeID').append($(`<option value="${film.id}">${film.brand} ${film.name} ${film.iso}</option>`));
      });
    },
  });
}

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

// Helper Functions
function formatDate(date) {
  if (date) {
    const newDate = new Date(date);
    return $.datepicker.formatDate('yy-mm-dd', newDate);
  }
  return 'Unknown';
}

function isKnown(item) {
  if (item) {
    return item;
  }
  return 'Unknown';
}
