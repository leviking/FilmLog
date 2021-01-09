/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const filmTypeID = currentURL.split('/')[4];
const filmTestID = currentURL.split('/')[6];

let filmName;

function generateHDCurve(steps) {
  let canvas = $('#hdCurve');
  let data = [];

  $.each(steps, (i, step) => {
    data.push({
      x: step.logE,
      y: step.filmDensity,
    });
  });
  console.log(data);

  let hdCurve = new Chart(canvas, {
    type: 'scatter',
    data: {
        datasets: [{
          label: filmName,
          data: data,
          showLine: true,
          fill: false,
          //borderColor: "#882222"
          borderColor: `#${Math.floor(Math.random()*16777215).toString(16)}`
        }]
    },
    options: {
      cubicInterpolationMode: 'default',
      legend: {
        position: 'bottom'
      },
      scales: {
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Density'
          }
        }],
        xAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Log'
          }
        }]
      }
    }
  });
}

function getFilm() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/films/${filmTypeID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const film = data.data;
      filmName = film.name;
      $('#name').append(`${film['name']} ${film['iso']} Film Test`);
    },
  });
}

function getFilmTest() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/films/${filmTypeID}/tests/${filmTestID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const test = data.data;
      $('#testedOn').append(formatDate(test.testedOn));
      $('#filmSize').append(test.filmSize);
      $('#developer').append(test.developer);
      $('#devTime').append(test.devTime);
      $('#baseFog').append(test.baseFog);
      $('#dMax').append(test.dMax);
      $('#gamma').append(test.gamma);
      $('#contrastIndex').append(test.contrastIndex);
      $('#kodakISO').append(test.kodakISO);
      if (test.notes) {
        $('#notesDiv').prop('hidden', false);
        $('#notes').append(test.notes);
      }
    },
  });
}

function getFilmTestSteps() {
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/films/${filmTypeID}/tests/${filmTestID}/steps`,
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
          row += `<td>${steps[i].logE}</td>`;
          row += `<td><input type="number" id="filmDensity${i}" min="0" max="9" `;
          row += `step="0.01" value="${steps[i].filmDensity}" /></td>`;
          $('#stepsTableBody').append($(row));
        }
        generateHDCurve(steps);
      } else {
        for (i=0; i < 21; i++)
        {
          let row = `<tr id="stepNumber:${i}">`;
          row += `<td>${i+1}</td>`;
          row += `<td>0</td>`;
          row += `<td><input type="number" id="filmDensity${i}" min="0" max="9" `;
          row += `step="0.01" value="0" /></td>`;
          $('#stepsTableBody').append($(row));
        }
      }
    },
    });
  }

function updateTestSteps() {

  let steps = {
    data: []
  }
  for (i=0; i < 21; i++) {
    let step = {
      "stepNumber": i+1,
      "filmDensity" : $(`#filmDensity${i}`).val()
    }
    steps['data'].push(step);
  }
  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/films/${filmTypeID}/tests/${filmTestID}/steps`,
    data: JSON.stringify(steps),
    contentType: 'application/json',
    dataType: 'json',
    statusCode: {
      204() {
        getFilmTestSteps();
      },
      400() { showAlert('Cannot Update Steps', 'Bad data', 'danger'); },
    },
  });
}


$(document).ready(() => {
  getFilm();
  getFilmTest();
  getFilmTestSteps();
});

// Add Film on form submission
$('#stepsForm').on('submit', (e) => {
  e.preventDefault();
  updateTestSteps();
});
