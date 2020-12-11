/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const cameraID = currentURL.split('/')[5];

let camera = null;

// Make a call to get camera details
function getCamera() {
  // Get camera details
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/cameras/${cameraID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      camera = data.data;
      $('#cameraName').html(camera.name);
      $('#status').html(camera.status);
      $('#filmSize').html(camera.filmSize);
      $('#integratedShutter').html(camera.integratedShutter);
      if (camera.filmLoaded) {
        $('#filmLoadedName').html(camera.filmLoaded.name);
        $('#filmLoadedISO').html(camera.filmLoaded.iso);
      } else {
        $('#filmLoadedName').html('None');
        $('#filmLoadedISO').html('');
      }
      if (camera.notes) {
        $('#notes').html(camera.notes);
      } else {
        $('#noteDiv').prop('hidden', true);
      }
      $('#lenses').empty();
      $.each(camera.lenses, (i, lens) => {
        $('#lenses').append($(`<li>${lens.name}</li>`));
      });
      if (camera.integratedShutter === 'Yes' && camera.shutterSpeeds.length > 0) {
        $('#shutterSpeedsTableBody').empty();
        $('#shutterSpeedsDiv').prop('hidden', false);
        $.each(camera.shutterSpeeds, (i, speed) => {
          let row = `<tr id="speed${speed.speed}">`;
          row += `<td>1/${speed.speed}</td>`;
          row += `<td>1/${speed.measuredSpeed}</td>`;
          row += `<td>${speed.idealSpeedMicroseconds}</td>`;
          row += `<td>${speed.measuredSpeedMicroseconds}</td>`;
          row += `<td>${speed.differenceStops}</td>`;
          row += '</tr>';
          $('#shutterSpeedsTableBody').append($(row));
          shutterSpeedDifferenceCSS(speed.differenceStops, `#speed${speed.speed}`);
        });
      }
    },
  });
}

// Load film into camera
function loadFilm() {
  const filmTypeID = $('#filmType').val();

  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/cameras/${cameraID}/loadFilm/${filmTypeID}`,
    contentType: 'application/json',
    statusCode: {
      200() {
        getCamera();
        $('#loadFilmForm')[0].reset();
        window.scrollTo(0, 0);
      },
      400() { showAlert('Cannot Load Film', 'Bad data', 'danger'); },
    },
  });
}

$(document).ready(() => {
  getCamera();
  getFilmTypes();
});

// Load Film on form submission
$('#loadFilmForm').on('submit', (e) => {
  e.preventDefault();
  loadFilm();
});
