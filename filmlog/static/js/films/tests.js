
function getFilmTests() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/films/tests',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const tests = data.data;


      $('#filmTestsTableBody').empty();
      $.each(tests, (i, test) => {
        let createdOn = formatDate(test.testedOn);
        let row = `<tr id="filmTestID:${test.id}">`;
        row += `<td>${test.filmName} ${test.iso}</td>`;
        row += `<td>${test.filmSize}</td>`;
        row += `<td>${test.developer}</td>`;
        row += `<td>${test.devTime}</td>`;
        row += `<td>${test.baseFog}</td>`;
        row += `<td>${test.dMax}</td>`;
        row += `<td>${test.gamma}</td>`;
        row += `<td>${test.contrastIndex}</td>`;
        row += `<td>${test.kodakISO}</td>`;
        row += `<td>${createdOn}</td>`;
        row += `<td></td>`;
       row += '</tr>';
        $('#filmTestsTableBody').append($(row));
      });
    },
  });
}


$(document).ready(() => { getFilmTests(); });
