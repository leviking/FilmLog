/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const binderID = currentURL.split('/')[4];
const projectID = currentURL.split('/')[6];

/* Helper Functions */
// Helper function to create project rows in table
function displayFilmRow(film) {
  let filmType = '';
  let iso = '';

  if (film.iso) {
    iso = `at ${film.iso}`;
  }

  if (film.brand) {
    filmType = `${film.brand} ${film.film} ${film.box_speed} ${iso}`;
  }

  let row = `<tr id="rowFilmID${film.id}">`;
  row += `<td><a href="/binders/${binderID}/projects/${projectID}/films/${film.id}">${film.title}</a></td>`;
  row += `<td>${film.file_no}</td>`;
  row += `<td>${film.exposures}</td>`;
  row += `<td>${film.size}</td>`;
  row += `<td>${filmType}</td>`;
  row += `<td><button class="btn btn-danger" name="button" value="Delete" \
             onclick="deleteFilm(${film.id})">Delete</button></td>`;
  $('#filmsTableBody').append($(row));
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
    },
    statusCode: { 403() { showAlert('Cannot Delete Film', 'It has films in it.', 'danger'); } },
  });
}

/* Ajax and Events */
// Make a call to pull a the current binder the projects reside under
jQuery.ajax({
  type: 'GET',
  url: `/api/v1/binders/${binderID}/projects/${projectID}`,
  contentType: 'application/json',
  dataType: 'json',
  success(data) {
    $('#projectName').html(data.data.name);
  },
});

// Make a call for the projcts under the current binder
jQuery.ajax({
  type: 'GET',
  url: `/api/v1/binders/${binderID}/projects/${projectID}/films`,
  contentType: 'application/json',
  dataType: 'json',
  success(data) {
    jQuery(data.data).each((i, film) => { displayFilmRow(film); });
  },
});
