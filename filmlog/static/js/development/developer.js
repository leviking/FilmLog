/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const developerID = currentURL.split('/')[5];
const days = 30;
let lastLogDate = subtractDays($.datepicker.formatDate('yy/mm/dd', new Date()), 30);

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
function getLogs(startDate = null, endDate = null) {
  let url = `/api/v1/development/developers/${developerID}/logs`;
  if (startDate && endDate) {
    url += `?startDate=${startDate}&endDate=${endDate}`;
  } else if (startDate) {
    url += `?startDate=${startDate}`;
  } else if (endDate) {
    url += `?endDate=${endDate}`;
  }

  jQuery.ajax({
    type: 'GET',
    url: url,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      logs = data.data;
      pagination = data.pagination;

      if (logs.length > 0) {
        lastLogDate = logs[logs.length-1].logged_on;

        logs.forEach((log) => {
          let films = '';
          log.films.forEach((film) => {
            let comp = '';
            if (film.compensation) {
              if (film.compensation > 0) {
                comp = `+${film.compensation}`;
              } else {
                comp = `-${film.compensation}`;
              }
            }
            films += `${film.qty}x ${film.name} ${film.iso} ${comp} in ${film.size}<br />`;
          });

          let row = '<tr>';
          row += `<td><a href="/developing/developer/${developerID}/log/${log.id}">${formatDate(log.logged_on)}</a></td>`;
          row += `<td>${nullToEmpty(log.ml_replaced)}</td>`;
          row += `<td>${nullToEmpty(log.ml_used)}</td>`;
          row += `<td>${nullToEmpty(films)}</td>`;
          row += `<td>${nullToEmpty(log.dev_time)}</td>`;
          row += `<td>${nullToEmpty(log.temperature)}</td>`;
          row += `<td class="devNotes">${nullToEmpty(log.notes)}</td></tr>`;

          $('#logsTableBody').append($(row));
        });
      } else {
        // If we didn't find any logs, bump up the last log date
        // in case the user wants to look further back.
        // There should be a better way to do this since we can easily
        // find out what the oldest log is, but it works for now.
        lastLogDate = subtractDays(lastLogDate, days);
        // $('#moreLogsLink').remove();
      }
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
        row += `<td>${film.name} ${film.iso}</td>`;
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

function getMoreLogs() {
  let startDate = subtractDays(lastLogDate, days);
  let endDate = formatDateTime(lastLogDate);
  console.log(startDate);
  console.log(endDate);
  logs = getLogs(startDate, endDate);
}

$(document).ready(() => {
  getDeveloper();
  //getLogs(subtractDays($.datepicker.formatDate('yy/mm/dd', new Date()), days), $.datepicker.formatDate('yy/mm/dd', new Date()));
  getLogs(subtractDays($.datepicker.formatDate('yy/mm/dd', new Date()), days), null);
  getFilmStats();
});

//'2019-01-01'
// if you are using datepicker . then dateValue = $.datepicker.parseDate("mm/dd/yy", '06/01/2012'); dateValue.setDate(dateValue.getDate()+1); – Priyank Patel Jun 7 '12 at 12:08
