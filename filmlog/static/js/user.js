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
        preferences += '<td><strong>Auto Update Film Stock</strong></td>';
        preferences += `<td><select id="autoUpdateFilmStockSelect" onchange='changeAutoUpdateFilmStock()'>`;
        if (data.autoUpdateFilmStock === 'Yes') {
          preferences += '<option value="No">No</option>';
          preferences += '<option value="Yes" selected>Yes</option>';
        } else {
          preferences += '<option value="No" selected>No</option>';
          preferences += '<option value="Yes">Yes</option>';
        }
        preferences += '</select></td></tr>';
        $('#preferencesTableBody').append($(preferences));
    }
  });
}

function changeAutoUpdateFilmStock() {
  // alert($('#autoUpdateFilmStockSelect').val());
    const data = {
      data: {
        name: 'autoUpdateFilmStock',
        value: $('#autoUpdateFilmStockSelect').val()
      }
    };
  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/user/preferences`,
    data: JSON.stringify(data),
    contentType: 'application/json',
    dataType: 'json'
    // success: updateHolderState(holderID, state),
  });
}


$(document).ready(() => { getPreferences(); });

// Add Holder on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
});
