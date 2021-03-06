/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const binderID = currentURL.split('/')[4];
const projectID = currentURL.split('/')[6];

let numFilms = 0;

// Helper function to display no films found message
function noFilmsFound() {
  noRowsFound('#filmsTableBody', 6, 'Films');
}

/* Helper Functions */
// Helper function to create project rows in table
function displayFilmRow(film) {
  let filmType = '';
  let iso = '';
  let boxSpeed = '';

  if (film.iso) {
    iso = `at ${film.iso}`;
  }

  if (film.film_type.film === 'Multiple') {
    boxSpeed = '';
    iso = '';
  } else {
    boxSpeed = film.film_type.box_speed;
  }

  if (film.film_type.film) {
    filmType = `${film.film_type.film} ${boxSpeed} ${iso}`;
  }

  let row = `<tr id="rowFilmID${film.id}">`;
  row += `<td><a href="/binders/${binderID}/projects/${projectID}/films/${film.id}">${film.title}</a></td>`;
  row += `<td>${film.file_no}</td>`;
  row += `<td>${film.exposures}</td>`;
  row += `<td>${film.size}</td>`;
  row += `<td>${filmType}</td>`;
  row += `<td><button class="btn btn-danger btn-sm" name="button" value="Delete" \
             onclick="deleteFilm(${film.id})">Delete</button></td>`;
  $('#filmsTableBody').append($(row));
}

/* Manipulation functions */

function getFilms() {
  $('#filmsTableBody').empty();

  // Make a call for the films under the current project
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/binders/${binderID}/projects/${projectID}/films`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      if (data.data.length > 0) {
        jQuery(data.data).each((i, film) => { displayFilmRow(film); });
      } else {
        noFilmsFound();
      }
    },
  });
}

function addFilm() {
  const film = {
    data: {
      title: $('#title').val(),
      fileNo: $('#fileNo').val(),
      fileDate: $('#fileDate').val(),
      filmSizeID: $('#filmSize').val(),
      filmTypeID: $('#filmType').val(),
      shotISO: $('#shotISO').val(),
      cameraID: $('#cameraID').val(),
      loaded: $('#loaded').val(),
      unloaded: $('#unloaded').val(),
      developed: $('#developed').val(),
      development: $('#development').val(),
      notes: $('#notes').val(),
    },
  };

  jQuery.ajax({
    type: 'POST',
    url: `/api/v1/binders/${binderID}/projects/${projectID}/films`,
    data: JSON.stringify(film),
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      // We re-generate the table so it sorts properly
      getFilms(data.data);
      $('#filmForm')[0].reset();
      numFilms += 1;
    },
    statusCode: { 409() { showAlert('Cannot Add Film', 'It already exists', 'warning'); } },
  });
}

// This function is used on the HTML side
// eslint-disable-next-line no-unused-vars
function deleteFilm(filmID) {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/binders/${binderID}/projects/${projectID}/films/${filmID}`,
    contentType: 'application/json',
    dataType: 'json',
    success() {
      const tr = `#rowFilmID${filmID}`;
      $(tr).remove();
      numFilms -= 1;
      if (numFilms === 0) {
        noFilmsFound();
      }
    },
    statusCode: { 403() { showAlert('Cannot Delete Film', 'It has films in it.', 'danger'); } },
  });
}

// This function is used on the HTML side
// eslint-disable-next-line no-unused-vars
function updateProject() {
  const name = $('#projectNameInput').val();
  const notes = $('#projectNotesTextArea').val();
  const project = { data: { name, notes } };

  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/binders/${binderID}/projects/${projectID}`,
    data: JSON.stringify(project),
    contentType: 'application/json',
    dataType: 'json',
    statusCode: {
      204() {
        getProject(binderID, projectID);
        window.scrollTo(0, 0);
      },
      400() { showAlert('Cannot Update Project', 'Bad data', 'danger'); },
    },
  });
}

// Delete Film
// Called from HTML
// eslint-disable-next-line no-unused-vars
function deleteProject() {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/binders/${binderID}/projects/${projectID}`,
    contentType: 'application/json',
    dataType: 'json',
    success() {
      window.location.replace(`/binders/${binderID}/projects`);
    },
  });
}

$(document).ready(() => {
  /* Fancy Calendar */
  $('#fileDate').datepicker({ dateFormat: 'yy-mm-dd' });
  $('#loaded').datepicker({ dateFormat: 'yy-mm-dd' });
  $('#unloaded').datepicker({ dateFormat: 'yy-mm-dd' });
  $('#developed').datepicker({ dateFormat: 'yy-mm-dd' });

  /* Get some things */
  getProject(binderID, projectID);
  getFilmSizes();
  getFilmTypes();

  // Make a call to pull the user's active cameras
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/cameras?status=Active',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $('#cameraID').append($('<option value="0">None</option>'));

      jQuery(data.data).each((i, camera) => {
        $('#cameraID').append($(`<option value="${camera.id}">${camera.name}</option>`));
      });
    },
  });

  getFilms();
  $('#editProjectForm').submit(false);
});

// Add Film on form submission
$('#filmForm').on('submit', (e) => {
  e.preventDefault();
  addFilm();
});
