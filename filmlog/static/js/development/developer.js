/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const developerID = currentURL.split('/')[5];

// Make a call to pull a list of all the user's developers
function getDeveloper() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/development/developers/${developerID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      developer = data.data;
      $('#developerName').html(developer['name']);
      $('#mixedOn').html(formatDate(developer['mixed_on']));
      $('#age').html(developer['days_old']);
      $('#type').html(developer['type']);
      $('#kind').html(developer['kind']);

      if (developer['kind'] === 'Replenishment') {
        $('#lastReplenished').html(`${developer['last_replenished']} days ago`);
        $('#lastReplenishedUl').show();
      }

      $('#state').html(developer['state']);
      if (developer['state'] == 'Retired') {
        $('#state').addClass('developerRetired');
      }

      if (developer['capacity'] > 1000) {
        $('#capacity').html(`${developer['capacity'] / 1000} L`)
      } else {
        $('#capacity').html(`${developer['capacity']} mL`)
      }

      if (developer['state'] == 'Active') {
        $('#developerButton').addClass('btn-warning');
        $('#developerButton').attr('value', 'retireDeveloper');
        $('#developerButton').append('Retire');
      } else {
        $('#developerButton').addClass('btn-success');
        $('#developerButton').attr('value', 'unretireDeveloper');
        $('#developerButton').append('Unretire');
      }

      if (developer['notes']) {
        $('#notesDiv').show();
        $('#notes').html(developer['notes']);
      }
    },
  });
}

$(document).ready(() => {
  getDeveloper();
});
