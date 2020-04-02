// Make a call to pull user's films

// Find Paper Row
function findPaperRow(paperID) {
  // CSS.escape to add slashes to the colon stuff (was a pain to figure out)
  const row = CSS.escape(`rowFilmType:${paperID}`);
  return `#${row}`;
}

// Delete Film Row
function deletePaperRow(paperID) {
  const tr = findPaperRow(paperID);
  $(tr).remove();
}

function getPapers() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/papers',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const papers = data.data;
      $('#papersTableBody').empty();
      $.each(papers, (i, paper) => {
        let row = `<tr id="rowFilmType:${paper.id}">`;
        row += `<td>${paper.name}</td>`;
        row += `<td>${paper.type}</td>`;
        row += `<td>${paper.grade}</td>`;
        row += `<td>${paper.surface}</td>`;
        row += `<td>${paper.tone}</td>`;
        row += `<td>${paper.prints}</td>`;
        row += `<td><button name="button" value="delete" class="btn btn-sm btn-danger" \
                 onclick="deleteFilmType('${paper.id}', '${paper.count}')">Delete</button></td>`;
       row += '</tr>';
        $('#papersTableBody').append($(row));
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

$(document).ready(() => { getPapers(); });

// Add Film on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
  addFilmType();
});
