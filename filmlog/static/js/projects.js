/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const binderID = currentURL.split('/')[4];

/* Helper Functions */
// Helper function to create project rows in table
function displayProjectRow(project) {
  const created_on = formatDate(project.created_on);

  let row = `<tr id="rowProjectID${project.id}">`;
  row += `<td><a href="/binders/${binderID}/projects/${project.id}">${project.name}</a></td>`;
  row += `<td>${project.film_count}</td>`;
  row += `<td>${created_on}</td>`;
  row += `<td><button class="btn btn-danger" name="button" value="Delete" \
             onclick="deleteProject(${project.id})">Delete</button></td>`;
  $('#projectsTableBody').append($(row));
}


/* Manipulation functions */
function addProject() {
  const name = $('#projectName').val();
  const project = { data: { name } };

  if (!$('#projectName').val()) {
    showAlert('Cannot Add Project', 'It needs a name.', 'danger');
    return;
  }

  jQuery.ajax({
    type: 'POST',
    url: `/api/v1/binders/${binderID}/projects`,
    data: JSON.stringify(project),
    contentType: 'application/json',
    dataType: 'json',
    success(data) { displayProjectRow(data.data); },
    statusCode: { 409() { showAlert('Cannot Add Project', 'It already exists.', 'warning'); } },
  });
  $('#projectForm')[0].reset();
}

// This function is used on the HTML side
// eslint-disable-next-line no-unused-vars
function deleteProject(projectID) {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/binders/${binderID}/projects/${projectID}`,
    contentType: 'application/json',
    dataType: 'json',
    success() {
      const tr = `#rowProjectID${projectID}`;
      $(tr).remove();
    },
    statusCode: { 403() { showAlert('Cannot Delete Project', 'It has films in it.', 'danger'); } },
  });
}

/* Ajax and Events */
// Make a call to pull a the current binder the projects reside under
jQuery.ajax({
  type: 'GET',
  url: `/api/v1/binders/${binderID}`,
  contentType: 'application/json',
  dataType: 'json',
  success(data) { $('#binderName').html(data.data.name); },
});

// Make a call for the projcts under the current binder
jQuery.ajax({
  type: 'GET',
  url: `/api/v1/binders/${binderID}/projects`,
  contentType: 'application/json',
  dataType: 'json',
  success(data) {
    jQuery(data.data).each((i, project) => { displayProjectRow(project); });
  },
});

// Add Project on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
  addProject();
});
