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

$(document).ready(() => {
  getFilm();
  getFilmTests();
});
