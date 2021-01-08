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
      if (test.steps.length > 0) {
        $.each(test.steps, (i, step) => {
          let row = `<tr id="stepNumber:${step.stepNumber}">`;
          row += `<td>${step.stepNumber}</td>`;
          row += `<td>${step.logE}</td>`;
          row += `<td>${step.filmDensity}</td></tr>`;
          $('#stepsTableBody').append($(row));
        });
        generateHDCurve(test.steps);
      } else {
        let row = '<tr><td colspan="3">No Steps Entered</td></tr>';
        $('#stepsTableBody').append($(row));
      }
    },
  });
}

$(document).ready(() => {
  getFilm();
  getFilmTest();
});
