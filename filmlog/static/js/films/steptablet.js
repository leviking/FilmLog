/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const stepTabletID = currentURL.split('/')[5];

function getStepTablet() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/steptablets/${stepTabletID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const tablet = data.data;
      $('#name').text(tablet.name);
      $('#createdOn').text(tablet.createdOn);
    },
  });
}

function getStepTabletSteps() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/steptablets/${stepTabletID}/steps`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const steps = data.data;
      $(`#stepsTableBody`).empty();
      if (steps.length > 0) {
        for (i=0; i < 21; i++)
        {
          let row = `<tr id="stepNumber:${i}">`;
          row += `<td>${steps[i].stepNumber}</td>`;
          row += `<td><input type="number" id="stepDensity${i}" min="0" max="9" `;
          row += `step="0.01" value="${steps[i].stepDensity}" /></td>`;
          $('#stepsTableBody').append($(row));
        }
      } else {
        for (i=0; i < 21; i++)
        {
          let row = `<tr id="stepNumber:${i}">`;
          row += `<td>${i+1}</td>`;
          row += `<td><input type="number" id="stepDensity${i}" min="0" max="9" `;
          row += `step="0.01" value="0" /></td>`;
          $('#stepsTableBody').append($(row));
        }
      }
    },
    });
  }

function updateStepTabletSteps() {
  let steps = {
    data: []
  }
  for (i=0; i < 21; i++) {
    let step = {
      "stepNumber": i+1,
      "stepDensity" : $(`#stepDensity${i}`).val()
    }
    steps['data'].push(step);
  }
  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/steptablets/${stepTabletID}/steps`,
    data: JSON.stringify(steps),
    contentType: 'application/json',
    dataType: 'json',
    statusCode: {
      204() {
        getStepTabletSteps();
      },
      400() { showAlert('Cannot Update Steps', 'Bad data', 'danger'); },
    },
  });
}

$(document).ready(() => {
  getStepTablet();
  getStepTabletSteps();
});

// Add Film on form submission
$('#stepsForm').on('submit', (e) => {
  e.preventDefault();
  updateStepTabletSteps();
});
