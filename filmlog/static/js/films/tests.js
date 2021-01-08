function generateHDCurves(films) {
  let canvas = $('#hdCurves');
  let datasets = [];

  $.each(films, (i, film) => {
    let data = [];
    $.each(film.steps, (i, step) => {
      data.push({
        x: step.logE,
        y: step.filmDensity,
      });
    });
    let dataset = {
      label: `${film.filmName} ${film.iso}`,
      data: data,
      showLine: true,
      fill: false,
      borderColor: `#${Math.floor(Math.random()*16777215).toString(16)}`
    }
    datasets.push(dataset);
  });

  console.log(datasets);

  let hdCurve = new Chart(canvas, {
    type: 'scatter',
    data: {
        datasets: datasets,
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

function getFilmTestCurves() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/films/tests/curves',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      generateHDCurves(data.data);
    }
  });
}

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

$(document).ready(() => {
  getFilmTests();
  getFilmTestCurves();
});
