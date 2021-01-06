// Make a call to pull user's preferences

// Find Film Row
function findFilmRow(filmTypeID) {
  // CSS.escape to add slashes to the colon stuff (was a pain to figure out)
  const row = CSS.escape(`rowFilmType:${filmTypeID}`);
  return `#${row}`;
}

// Delete Film Row
function deleteFilmRow(filmTypeID) {
  const tr = findFilmRow(filmTypeID);
  $(tr).remove();
}

function getFilms() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/films',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const films = data.data;
      $('#filmsTableBody').empty();
      $.each(films, (i, film) => {
        let row = `<tr id="rowFilmType:${film.id}">`;
        row += `<td>${film.name}</td>`;
        row += `<td>${film.iso}</td>`;
        row += `<td>${film.kind}</td>`;
        row += `<td>${film.count}</td>`;
        row += `<td><button name="button" value="delete" class="btn btn-sm btn-danger" \
                 onclick="deleteFilmType('${film.id}', '${film.count}')">Delete</button></td>`;
       row += '</tr>';
        $('#filmsTableBody').append($(row));
      });
    },
  });
}

/* Manipulation Functions */
function addFilmType() {
  const name = $('#filmName').val();
  const iso = $('#filmISO').val();
  const kind = $('#filmKind').val()
  const newFilmType = { data: {
      name: name,
      iso: iso,
      kind: kind}};

  jQuery.ajax({
    type: 'POST',
    url: '/api/v1/films',
    data: JSON.stringify(newFilmType),
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      getFilms();
      $('#filmTypeForm')[0].reset();
      window.scrollTo(0, 0);
    },
    statusCode: {
      400() { showAlert('Cannot Add Film Type', 'Bad data', 'danger'); },
      409() { showAlert('Cannot Add Film Type', 'It already exists', 'danger'); } },
  });
}

function deleteFilmType(filmTypeID, count) {
  if(count > 0) {
    showAlert('Cannot Delete Film', 'It has logged films associated with it', 'danger');
    return;
  }
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/films/${filmTypeID}`,
    contentType: 'application/json',
    dataType: 'json',
    success: deleteFilmRow(filmTypeID),
  });
}

$(document).ready(() => { getFilms(); });

// Add Film on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
  addFilmType();
});
