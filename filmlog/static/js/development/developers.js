
// Make a call to pull a list of all the user's developers
function getDevelopers() {
  $('#developersTableBody').empty();
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/development/developers/',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      jQuery(data.data).each((i, developer) => {
        if(developer['state'] === 'Active') {
          $("#activeDevelopers").append(`<li> \
            <a href="/developing/developer/${developer['id']}"> \
            ${developer['name']}</a> - \
            ${developer['type']} ${developer['kind']}</li>`)
        } else {
          $("#retiredDevelopers").append(`<li> \
            <a href="/developing/developer/${developer['id']}"> \
            ${developer['name']}</a> - \
            ${developer['type']} ${developer['kind']}</li>`)
        }
      });
      if ($("#retiredDevelopers").is(':empty')) {
        $("#retiredDevelopersHeading").remove();
      }
    },
  });
}

$(document).ready(() => {
  getDevelopers();
});
