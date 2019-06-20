// Helper function to create binder rows in table
function displayBinderRow(binder) {
  let row = `<tr id="rowBinderID${binder.id}">`;
  row += `<td><a href="/binders/${binder.id}/projects">${binder.name}</a></td>`;
  row += `<td>${binder.project_count}</td>`;
  row += `<td>${binder.created_on}</td>`;
  row += `<td><button class="btn btn-danger" name="button" value="Delete" \
             onclick="deleteBinder(${binder.id})">Delete</button></td>`;
  $('#bindersTableBody').append($(row));
}

/* Manipulation functions */
function addBinder() {
  const name = $('#binderName').val();
  const binder = { data: { name } };

  if (!$('#binderName').val()) {
    showAlert('Cannot Add Binder', 'It needs a name.', 'danger');
    return;
  }

  jQuery.ajax({
    type: 'POST',
    url: '/api/v1/binders',
    data: JSON.stringify(binder),
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      displayBinderRow(data.data);
      $('#binderForm')[0].reset();
    },
    statusCode: { 409() { showAlert('Cannot Add Binder', 'It already exists', 'danger'); } },
  });
}

// This function is used on the HTML side
// eslint-disable-next-line no-unused-vars
function deleteBinder(binderID) {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/binders/${binderID}`,
    contentType: 'application/json',
    dataType: 'json',
    success() {
      const tr = `#rowBinderID${binderID}`;
      $(tr).remove();
    },
    // eslint-disable-next-line no-unused-vars
    statusCode: { 403() { showAlert('Cannot Remove Binder', 'Binder has projects in it.', 'warning'); } },
  });
}

/* Ajax and Events */
jQuery.ajax({
  type: 'GET',
  url: '/api/v1/binders',
  contentType: 'application/json',
  dataType: 'json',
  success(data) {
    jQuery(data.data).each((i, binder) => { displayBinderRow(binder); });
  },
});

// Add Binder on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
  addBinder();
});
