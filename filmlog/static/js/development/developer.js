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

// Make a call to grab the logs, not this is where we will need to
// figure out pagination
function getLogs() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/development/developers/${developerID}/logs`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      logs = data.data;
      pagination = data.pagination;

      logs.forEach((log) => {
        let films = '';
        log.films.forEach((film) => {
          films += `${film.qty}x ${film.brand} ${film.name} in ${film.size}<br />`;
        });

        let row = '<tr>';
        row += `<td><a href="/developing/developer/${developerID}/log/${log.id}">${formatDate(log.logged_on)}</a></td>`;
        row += `<td>${nullToEmpty(log.ml_replaced)}</td>`;
        row += `<td>${nullToEmpty(log.ml_used)}</td>`;
        row += `<td>${nullToEmpty(films)}</td>`;
        row += `<td>${nullToEmpty(log.dev_time)}</td>`;
        row += `<td>${nullToEmpty(log.temperature)}</td>`;
        row += `<td>${nullToEmpty(log.notes)}</td>`;

        $('#logsTableBody').append($(row));
      });
    },
  });
}

// Make a call to grab some film stats
function getFilmStats() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/development/developers/${developerID}/stats`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      films = data.data.films;
      sizes = data.data.sizes;

      films.forEach((film) => {
        let row = `<tr>`;
        row += `<td>${film.size}</td>`;
        row += `<td>${film.brand} ${film.name} ${film.iso}</td>`;
        row += `<td>${film.qty}</td>`;
        row += `</tr>`;

        $('#filmsTableBody').append($(row));
      });

      sizes.forEach((size) => {
        let row = `<tr>`;
        row += `<td>${size.size}</td>`;
        row += `<td>${size.qty}</td>`;
        row += `<td>${size.adjusted_qty}</td>`;
        row += `</tr>`;

        $('#sizesTableBody').append($(row));
      });

    },
  });
}

$(document).ready(() => {
  getDeveloper();
  getLogs();
  getFilmStats();
});
