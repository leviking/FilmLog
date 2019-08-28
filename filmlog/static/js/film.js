/* Figure out the URL parameters */
const currentURL = $(location).attr('href');
const binderID = currentURL.split('/')[4];
const projectID = currentURL.split('/')[6];
const filmID = currentURL.split('/')[8];

function getFilm() {
  // Make a call for the films under the current project
  jQuery.ajax({
    type: 'GET',
    url: `/api/v1/binders/${binderID}/projects/${projectID}/films/${filmID}`,
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      const film = data.data;
      $('#title').html(film.title);
      $('#camera').html(isKnown(film.camera.name));
      $('#file_date').html(formatDate(film.file_date));
      $('#file_no').html(film.file_no);

      if (film.loaded || film.unloaded || film.developed) {
        $('#loaded').html(formatDate(film.loaded));
        $('#unloaded').html(formatDate(film.unloaded));
        $('#developed').html(formatDate(film.developed));
      } else {
        $('#divFilmDates').remove();
      }

      if (film.film_type.film) {
        $('#filmType').html(`${film.film_type.brand} ${film.film_type.film}`);
        $('#filmSize').html(film.size);
        $('#filmISO').html(`${film.film_type.box_speed}, shot at ${film.iso}`);
      } else {
        $('#divFilmType').remove();
      }

      if (film.development) {
        $('#development').html(film.development);
      } else {
        $('#divDevelopment').remove();
      }
    },
  });
}

$(document).ready(() => {
  getProject(binderID, projectID);
  getFilm();
});
