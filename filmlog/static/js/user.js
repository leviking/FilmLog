// Make a call to pull user's preferences
function getPreferences() {
  $('#userPreferences').empty();
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/user/preferences',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      let preferenceData = data.data;

      let preferences = '<tr id="autoUpdateFilmStock">';
        preferences += '<th>Auto Update Film Stock</th>';
        preferences += `<td>${data.autoUpdateFilmStock}</td>`;
        preferences += '</td></tr>';
        $('#preferencesTableBody').append($(preferences));
    }
  });
}

$(document).ready(() => { getPreferences(); });

// Add Holder on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
  // addHolder();
});
