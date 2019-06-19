/* Figure out the URL parameters */
var current_url = $(location).attr("href");
var binderID = current_url.split('/')[4];

/* Ajax and Events */
// Make a call to pull a the current binder the projects reside under
jQuery.ajax({
  type: "GET",
  url: "/api/v1/binders/" + binderID,
  contentType: "application/json",
  dataType: "json",
  success: function(data) { $("#binderName").html(data.data.name); }
});

// Make a call for the projcts under the current binder
jQuery.ajax({
  type: "GET",
  url: "/api/v1/binders/" + binderID + "/projects",
  contentType: "application/json",
  dataType: "json",
  success(data) {
    jQuery(data.data).each((i, project) => { displayProjectRow(project); });
  },
});

// Add Project on form submission
$("form").on("submit", function (e)
{
  e.preventDefault();
  addProject();
  $("#projectForm")[0].reset();
});

/* Manipulation functions */
function addProject()
{
  var name = $('#projectName').val();
  var project =
  {
    "data" :
    {
      "name": name,
    }
  }

  jQuery.ajax({
    type: "POST",
    url: "/api/v1/binders/" + binderID + "/projects",
    data: JSON.stringify(project),
    contentType: "application/json",
    dataType: "json",
    success: function(data) {
      displayProjectRow(data.data);
    },
    statusCode:
    {
      409: function() { alert( 'Project already exists' ); },
    }
  });
}

function deleteProject(projectID)
{
  jQuery.ajax({
    type: "DELETE",
    url: "/api/v1/binders/" + binderID + "/projects/" + projectID,
    contentType: "application/json",
    dataType: "json",
    success() {
      const tr = `#rowProjectID${projectID}`;
      $(tr).remove();
    },
    statusCode:
    {
      403: function() { alert( 'Cannot delete project with films in it.' ); }
    }
  });
}

/* Helper Functions */
// Helper function to create project rows in table
function displayProjectRow(project)
{
  var row = '<tr id="rowProjectID' + project.id + '">';
  row += '<td><a href="/binders/' + binderID + '/projects/' + project.id + '">' + project.name + '</a></td>';
  row += '<td>' + project.film_count + '</td>';
  row += '<td>' + project.created_on + '</td>';
  row += '<td><button class="btn btn-danger" name="button" value="Delete" \
             onclick="deleteProject(' + project.id + ')">Delete</button></td>';
  $('#projectsTableBody').append($(row));
}
