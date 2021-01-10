function getStepTablets() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/steptablets',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const tablets = data.data;
      $('#stepTabletsBody').empty();
      if (tablets.length > 0) {
        $.each(tablets, (i, tablet) => {
          let createdOn = formatDate(tablet.createdOn);
          let row = `<tr id="stepTabletID:${tablet.stepTabletID}">`;
          row += `<td><a href="/films/steptablets/${tablet.stepTabletID}">${tablet.name}</a></td>`;
          row += `<td>${createdOn}</td>`;
          row += `<td><button class="btn btn-danger btn-sm" name="button" value="Delete" \
                     onclick="deleteStepTablet(${tablet.stepTabletID})">Delete</button></td></tr>`;
          $('#stepTabletsBody').append($(row));
        });
      } else {
        $('#stepTabletsBody').append('<tr><td colspan="2">No Tests Made</td></tr>');
      }
    },
  });
}

function addStepTablet() {
  const tablet = {
    data: {
      name: $('#stepTabletName').val(),
    },
  };

  jQuery.ajax({
    type: 'POST',
    url: '/api/v1/steptablets',
    data: JSON.stringify(tablet),
    contentType: 'application/json',
    dataType: 'json',
    statusCode: {
        201() {
          getStepTablets();
          window.scrollTo(0, 0);
          $('#stepTabletForm')[0].reset();
        },
       409() { showAlert('Cannot Add Step Tablet', 'There was a problem.', 'warning'); } },
  });
}

function deleteStepTablet(stepTabletID) {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/steptablets/${stepTabletID}`,
    contentType: 'application/json',
    dataType: 'json',
    success() {
      getStepTablets();
    },
    statusCode: { 403() { showAlert('Cannot Delete Step Tablet', 'It may have associated film tests with it.', 'danger'); } },
  });
}

$(document).ready(() => {
  getStepTablets();
});

// Add Film on form submission
$('#stepTabletForm').on('submit', (e) => {
  e.preventDefault();
  addStepTablet();
});
