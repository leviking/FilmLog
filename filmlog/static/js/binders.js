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

  jQuery.ajax({
    type: 'POST',
    url: '/api/v1/binders',
    data: JSON.stringify(binder),
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      displayBinderRow(data.data);
    },
    statusCode: { 409() { alert('Binder already exists'); } },
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
    statusCode: { 403() { alert('Cannot delete binder with projects in it.'); } },
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
  $('#binderForm')[0].reset();
});
