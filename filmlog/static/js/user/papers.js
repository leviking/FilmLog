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
        row += `<td>${paper.numPrints}</td>`;
        row += `<td>${paper.numContactSheets}</td>`;
        row += `<td><button name="button" value="delete" class="btn btn-sm btn-danger" \
                 onclick="deletePaper('${paper.id}', '${paper.count}')">Delete</button></td>`;
       row += '</tr>';
        $('#papersTableBody').append($(row));
      });
    },
  });
}

/* Manipulation Functions */
function addPaper() {
  const name = $('#name').val();
  const type = $('#type').val();
  const grade = $('#grade').val();
  const surface = $('#surface').val();
  const tone = $('#tone').val();

  const newPaper = { data: {
      name: name,
      type: type,
      grade: grade,
      surface: surface,
      tone: tone }};

  jQuery.ajax({
    type: 'POST',
    url: '/api/v1/papers',
    data: JSON.stringify(newPaper),
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      getPapers();
      $('#paperForm')[0].reset();
      window.scrollTo(0, 0);
    },
    statusCode: {
      400() { showAlert('Cannot Add Paper', 'Bad data', 'danger'); },
      409() { showAlert('Cannot Add Paper', 'It already exists', 'danger'); } },
  });
}

function deletePaper(paperID) {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/papers/${paperID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      deletePaperRow(paperID);
      getPapers();
      window.scrollTo(0, 0);
    },
    statusCode: {
      403() { showAlert('Cannot Delete Paper', 'It may have prints and contact sheets associated with it', 'danger'); } },
  });
}

$(document).ready(() => { getPapers(); });

// Add Film on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
  addPaper();
});
