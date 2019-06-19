/* Ajax and Events */
// Make a call to pull a list of all the user's binders
jQuery.ajax({
  type: "GET",
  url: "/api/v1/binders",
  contentType: "application/json",
  dataType: "json",
  success: function(data)
  {
    jQuery(data.data).each(function(i, binder){
      displayBinderRow(binder);
    });
  }
});

// Add Binder on form submission
$("form").on("submit", function (e)
{
  e.preventDefault();
  addBinder();
  $("#binderForm")[0].reset();
});

/* Manipulation functions */
function addBinder()
{
  var name = $('#binderName').val();
  var binder =
  {
    "data" :
    {
      "name": name,
    }
  }

  jQuery.ajax({
    type: "POST",
    url: "/api/v1/binders",
    data: JSON.stringify(binder),
    contentType: "application/json",
    dataType: "json",
    success: function(data) { displayBinderRow(data.data); },
    statusCode:
    {
      409: function() { alert( 'Binder already exists' ); },
    }
  });
}

function deleteBinder(binderID)
{
  jQuery.ajax({
    type: "DELETE",
    url: "/api/v1/binders/" + binderID,
    contentType: "application/json",
    dataType: "json",
    success: function(data)
    {
      var tr = '#rowBinderID' + binderID;
      $(tr).remove();
    },
    statusCode:
    {
      403: function() { alert( 'Cannot delete binder with projects in it.' ); }
    }
  });
}

// Helper function to create binder rows in table
function displayBinderRow(binder)
{
  var row = '<tr id="rowBinderID' + binder.id + '">';
  row += '<td><a href="/binders/' + binder.id + '/projects">' + binder.name + '</a></td>';
  row += '<td>' + binder.project_count + '</td>';
  row += '<td>' + binder.created_on + '</td>';
  row += '<td><button class="btn btn-danger" name="button" value="Delete" \
             onclick="deleteBinder(' + binder.id + ')">Delete</button></td>';
  $('#bindersTableBody').append($(row));
}
