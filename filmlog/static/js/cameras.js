/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const cameraID = currentURL.split('/')[5];

// Make a call to get cameras
function getCameras() {
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/cameras',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const cameras = data.data;
      $('#camerasTableBody').empty();
      $.each(cameras, (i, camera) => {
        let row = `<tr id="camera:${camera.id}">`;
        row += `<td><a href="/gear/camera/${camera.id}">${camera.name}</a></td>`;
        row += `<td>${camera.filmSize}</td>`;
        if (camera.loadedFilmName) {
          row += `<td>${camera.loadedFilmName} ${camera.loadedFilmISO}</td>`;
        } else {
          row += '<td></td>';
        }
        row += `<td>${camera.status}</td>`;
       row += '</tr>';
        $('#camerasTableBody').append($(row));
      });
    },
  });
}

$(document).ready(() => { getCameras(); });
