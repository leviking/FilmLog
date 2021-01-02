/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const binderID = currentURL.split('/')[4];
let numProjects = 0;

// Helper function to display no projects found message
function noProjectsFound() {
  noRowsFound('#projectsTableBody', 4, 'Projects');
}

/* Helper Functions */
// Helper function to create project rows in table
function displayProjectRow(project) {
  const createdOn = formatDate(project.created_on);

  let row = `<tr id="rowProjectID${project.id}">`;
  row += `<td><a href="/binders/${binderID}/projects/${project.id}">${project.name}</a></td>`;
  row += `<td>${project.film_count}</td>`;
  row += `<td>${createdOn}</td>`;
  row += `<td><button class="btn btn-danger btn-sm" name="button" value="Delete" \
             onclick="deleteProject(${project.id})">Delete</button></td>`;
  $('#projectsTableBody').append($(row));
}

/* Manipulation functions */
function addProject() {
  const name = $('#projectNameInput').val();
  const notes = $('#projectNotesTextArea').val();
  const project = { data: { name, notes } };

  if (!$('#projectNameInput').val()) {
    showAlert('Cannot Add Project', 'It needs a name.', 'danger');
    return;
  }

  jQuery.ajax({
    type: 'POST',
    url: `/api/v1/binders/${binderID}/projects`,
    data: JSON.stringify(project),
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      if (numProjects === 0) {
        $('#projectsTableBody').empty();
      }
      displayProjectRow(data.data);
      $('#addProjectForm')[0].reset();
      numProjects += 1;
    },
    statusCode: { 409() { showAlert('Cannot Add Project', 'It already exists.', 'warning'); } },
  });
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
      numProjects -= 1;
      if (numProjects === 0) {
        noProjectsFound();
      }
    },
    statusCode: { 403() { showAlert('Cannot Delete Project', 'It has films in it.', 'danger'); } },
  });
}

/* Ajax and Events */
// Make a call to pull a the current binder the projects reside under
function getBinder() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/binders/${binderID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      $('#binderName').html(data.data.name);
      $('#binderNameInput').val(data.data.name);
      if (data.data.notes) {
        $('#binderNotes').html(data.data.notes);
        $('#binderNotesTextArea').html(data.data.notes);
        $('#binderNotesDiv').show();
      }
    },
  });
}

// Make a call for the projcts under the current binder
function getProjects() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/binders/${binderID}/projects`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      numProjects = data.data.length;
      if (numProjects > 0) {
        jQuery(data.data).each((i, project) => { displayProjectRow(project); });
      } else {
        noProjectsFound();
      }
    },
  });
}

// This function is used on the HTML side
// eslint-disable-next-line no-unused-vars
function updateBinder() {
  const name = $('#binderNameInput').val();
  const notes = $('#binderNotesTextArea').val();
  const binder = { data: { name, notes } };

  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/binders/${binderID}`,
    data: JSON.stringify(binder),
    contentType: 'application/json',
    dataType: 'json',
    statusCode: {
      204() {
        getBinder(binderID);
        window.scrollTo(0, 0);
      },
      400() { showAlert('Cannot Update Binder', 'Bad data', 'danger'); },
    },
  });
}

// This function is used on the HTML side
// eslint-disable-next-line no-unused-vars
function deleteBinder() {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/binders/${binderID}`,
    contentType: 'application/json',
    dataType: 'json',
    success() {
      window.location.replace('/binders');
    },
    // eslint-disable-next-line no-unused-vars
    statusCode: { 403() { showAlert('Cannot Remove Binder', 'Binder has projects in it.', 'warning'); } },
  });
}

$(document).ready(() => {
  getBinder();
  getProjects();
  $('#editBinderForm').submit(false);
});

// Add Project on form submission
$('#addProjectForm').on('submit', (e) => {
  e.preventDefault();
  addProject();
});
