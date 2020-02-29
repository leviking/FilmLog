/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const cameraID = currentURL.split('/')[5];


// Make a call to get camera details
function getCamera() {
  // Get camera details
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/cameras/${cameraID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const camera = data.data;
      $('#cameraName').append(camera.name);
      $('#status').append(camera.status);
      $('#filmSize').append(camera.filmSize);
      $('#integratedShutter').append(camera.integratedShutter);
      $.each(camera.lenses, (i, lens) => {
        $('#lenses').append($(`<li>${lens.name}</li>`));
      });
      if (camera.integratedShutter === 'Yes' && camera.shutterSpeeds.length > 0) {
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


$(document).ready(() => { getCamera(); });
