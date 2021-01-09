// Shared Functions for other JavaScript files
/* eslint no-unused-vars: 0 */

// Helper Function When No Items Are Found
function noRowsFound(dom, colspan, item) {
  $(dom).empty();
  $(dom).append($(`<tr><td colspan="${colspan}">No ${item} Found</td></tr>`));
}

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
      if (data.data.notes) {
        $('#projectNotesDiv').show();
        $('#projectNotes').html(data.data.notes);
      }

      $('#projectNameInput').val(data.data.name);
      $('#projectNotesTextArea').html(data.data.notes);
    },
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
      jQuery(data.data).each((i, size) => {
        $('#filmSize').append($(`<option value="${size.id}">${size.size}</option>`));
      });
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
      $('#filmType').append($('<option value="0">None</option>'));
      jQuery(data.data).each((i, film) => {
        $('#filmType').append($(`<option value="${film.id}">${film.name} ${film.iso}</option>`));
      });
    },
  });
}

function getEnlargers() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/enlargers',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $.each(data.data, (i, enlarger) => {
        $('#enlargerID').append($(`<option value="${enlarger.id}">${enlarger.name}</option>`));
      });
    },
  });
}

function getEnlargerLenses() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/enlargers/lenses',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $.each(data.data, (i, enlargerLens) => {
        $('#enlargerLensID').append($(`<option value="${enlargerLens.id}">${enlargerLens.name}</option>`));
      });
    },
  });
}

function getFilters() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/filters',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $.each(data.data, (i, filter) => {
        $('#filterID').append($(`<option value="${filter.id}">${filter.code}</option>`));
      });
    },
  });
}



// Land mine! We're setting values in the DOM directly because AJAX calls
// are async normally and you can't pass data back without using a global
// variable.
// https://stackoverflow.com/questions/16805306/jquery-return-ajax-result-into-outside-variable/16805366
function getStepTablets() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/steptablets',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $.each(data.data, (i, tablet) => {
        $('#stepTabletID').append($(`<option value="${tablet.id}">${tablet.name}</option>`));
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

function formatDateTime(datetime) {
  if (datetime) {
    const newDate = new Date(datetime);
    date = $.datepicker.formatDate('yy-mm-dd', newDate);
    return `${date} ${newDate.getHours()}:${newDate.getMinutes()}:${newDate.getSeconds()}`;
  }
  return 'Unknown';
}

function shutterSpeedDifferenceCSS(differenceStops, entity) {
  if (differenceStops >= -0.25 && differenceStops <= 0) {
    $(entity).addClass('shutterTestGood');
  } else if (differenceStops <= -0.25 && differenceStops > -0.50) {
    $(entity).addClass('shutterTestFair');
  } else if (differenceStops <= -50) {
    $(entity).addClass('shutterTestPoor');
  } else if (differenceStops >= 0 && differenceStops <= 0.25) {
    $(entity).addClass('shutterTestGood');
  } else if (differenceStops > 0.25 && differenceStops < 0.50) {
    $(entity).addClass('shutterTestFair');
  } else if (differenceStops >= 0.50) {
    $(entity).addClass('shutterTestPoor');
  }
}


function subtractDays(date, days) {
  const newDate = new Date(date);
  newDate.setDate(newDate.getDate() - days);
  return formatDateTime(newDate);
}

function isKnown(item) {
  if (item) {
    return item;
  }
  return 'Unknown';
}

function nullToEmpty(item) {
  if (item) {
    return item;
  }
  return '';
}
