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
  success: function(data)
  {
    jQuery(data.data).each(function(i, project){
      console.log(project);
      displayProjectRow(project);
    });
  }
});

/* Manipulation functions */
function deleteProject(projectID)
{
  jQuery.ajax({
    type: "DELETE",
    url: "/api/v1/binders/" + binderID + "/projects/" + projectID,
    contentType: "application/json",
    dataType: "json",
    success: function(data)
    {
      var tr = '#rowProjectID' + projectID;
      console.log(tr);
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
