/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const filmTypeID = currentURL.split('/')[4];

function getFilm() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/films/${filmTypeID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const film = data.data;
      $('#name').append(`${film['name']} ${film['iso']}`);
      $('#kind').append(film['kind']);
      $('#count').append(film['count']);
    },
  });
}

function getFilmTests() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/films/${filmTypeID}/tests`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const tests = data.data;
      if (tests.length > 0) {
        $('#filmTestsTableBody').empty();
        $.each(tests, (i, test) => {
          let createdOn = formatDate(test.testedOn);
          let row = `<tr id="filmTestID:${test.id}">`;
          row += `<td><a href="/films/${filmTypeID}/tests/${test.id}">${createdOn}</a></td>`;
          row += `<td>${test.filmSize}</td>`;
          row += `<td>${test.developer}</td>`;
          row += `<td>${test.devTime}</td>`;
          row += `<td>${test.baseFog}</td>`;
          row += `<td>${test.dMax}</td>`;
          row += `<td>${test.gamma}</td>`;
          row += `<td>${test.contrastIndex}</td>`;
          row += `<td>${test.kodakISO}</td>`;
          row += `<td></td>`;
          row += '</tr>';
          $('#filmTestsTableBody').append($(row));
        });
      } else {
        let row = '<tr><td colspan="9">No Tests Made</td></tr>';
        $('#filmTestsTableBody').append($(row));
      }
    },
  });
}

function addTest() {
  const test = {
    data: {
      enlargerID: $('#enlargerID').val(),
      enlargerLensID: $('#enlargerLensID').val(),
      headHeight: $('#headHeight').val(),
      filmSize: $('#filmSize').val(),
      stepTabletID: $('#stepTabletID').val(),
      lux: $('#lux').val(),
      fstop: $('#fstop').val(),
      exposureTime: $('#exposureTime').val(),
      filterID: $('#filterID').val(),
      developer: $('#developer').val(),
      devTime: $(`#devTime`).val(),
      devTemperature: $(`#devTemperature`).val(),
      prebath: $('#prebath').val(),
      stop: $('#stop').val(),
      agitation: $('#agitation').val(),
      rotaryRPM: $('#rotaryRPM').val(),
      notes: $('#notes').val(),
    },
  };
  console.log(test);

  jQuery.ajax({
    type: 'POST',
    url: `/api/v1/films/${filmTypeID}/tests`,
    data: JSON.stringify(test),
    contentType: 'application/json',
    dataType: 'json',
    statusCode: {
        201() {
          getFilmTests();
          window.scrollTo(0, 0);
          $('#filmTestForm')[0].reset();
        },
       409() { showAlert('Cannot Add Test', 'There was a problem.', 'warning'); } },
  });
}

$(document).ready(() => {
  getFilm();
  getFilmTests();
  getStepTablets();
  getEnlargers();
  getEnlargerLenses();
  getFilters();
  $('#filmTestForm').submit(false);
});

// Add Film on form submission
$('#filmTestForm').on('submit', (e) => {
  e.preventDefault();
  addTest();
});
