/* Helper Functions */
// Find Film Row
function findFilmRow(filmID) {
  // CSS.escape to add slashes to the colon stuff (was a pain to figure out)
  const row = CSS.escape(`rowFilm:${filmID}`);
  return `#${row}`;
}

// Find Film's Qty Table Cell
function findFilmQtyCell(filmID) {
  const cell = CSS.escape(`film:${filmID}:Qty`);
  return `#${cell}`;
}

// Update the film's row colors (CSS)
function updateFilmRowColor(filmID, qty) {
  const tr = findFilmRow(filmID);
  $(tr).removeClass();
  if (qty === 0) {
    $(tr).addClass('filmStockZero');
  } else if (qty < 0) {
    $(tr).addClass('filmStockNegative');
  }
}

// Update the film's quantity in the UI
function updateFilmQty(filmID, qty) {
  const td = findFilmQtyCell(filmID);
  $(td).html(qty);
  updateFilmRowColor(filmID, qty);
}

function buildFilmStockTable(title, div, stock) {
  let filmType;
  const tableID = `table${div}`;
  const tableBodyID = `tableBody${div}`;

  /* If we have no stock, just return as there is nothing to display.
     (We want to hide the header) */
  if (stock.length === 0) {
    return;
  }

  if (title === 'Sheets') {
    filmType = 'Sheets';
  } else {
    filmType = 'Rolls';
  }

  $(`#${div}`).append($(`<h3>${title}</h3>`));
  $(`#${div}`).append($(`<table class="table table-striped table-bordered" id="${tableID}"></table>`));
  $(`#${tableID}`).append($(`<thead class="thead-light"><th>Film</th><th>ISO</th><th>Size</th><th>${filmType}</th><th></th></thead>`));
  $(`#${tableID}`).append($(`<tbody id="${tableBodyID}"></tbody>`));

  jQuery(stock).each((i, item) => {
    let row = `<tr id="rowFilm:${item.id}">`;
    row += `<td>${item.type}</td>`;
    row += `<td>${item.iso}</td>`;
    row += `<td>${item.size}</td>`;
    row += `<td id="film:${item.id}:Qty">${item.qty}</td>`;
    row += `<td> \
            <button name="button" value="increment" class="btn btn-sm btn-primary" \
             onclick="incdecFilm('${item.id}', 'Increment')">Increment</button> \
            <button name="button" value="decrement" class="btn btn-sm btn-danger" \
             onclick="incdecFilm('${item.id}', 'Decrement')">Decrement</button> \
            <button type="button" class="btn btn-sm btn-dark" \
             onclick="deleteFilm('${item.id}')">Delete</button>`;
    row += '</tr>';
    $(`#${tableBodyID}`).append($(row));
    updateFilmRowColor(item.id, item.qty);
  });
}


// Build out the film stocks to produce tables for each film size
function buildStocks(data) {
  const film35mm = [];
  const filmMediumFormat = [];
  const filmSheets = [];

  // Split out film into groups by size
  jQuery(data.data).each((i, stock) => {
    if (stock.size.startsWith('35mm')) {
      film35mm.push(stock);
    } else if (stock.size === '120' || stock.size === '220') {
      filmMediumFormat.push(stock);
    } else if (stock.size === '4x5') {
      filmSheets.push(stock);
    }
  });

  buildFilmStockTable('35mm', 'film35mm', film35mm);
  buildFilmStockTable('Medium Format', 'filmMediumFormat', filmMediumFormat);
  buildFilmStockTable('Sheets', 'filmSheets', filmSheets);
}

function deleteFilmRow(filmID) {
  const tr = findFilmRow(filmID);
  $(tr).remove();
}

// Make a call to pull all of the user's filmstock
jQuery.ajax({
  type: 'GET',
  url: '/api/v1/filmstock',
  contentType: 'application/json',
  dataType: 'json',
  success: buildStocks,
});

/* Actions */
// Delete Film
// Called from HTML
// eslint-disable-next-line no-unused-vars
function deleteFilm(filmID) {
  jQuery.ajax({
    type: 'DELETE',
    url: `/api/v1/filmstock/${filmID}`,
    contentType: 'application/json',
    dataType: 'json',
    success: deleteFilmRow(filmID),
  });
}


// Increment/Decrement Film
// Called from HTML
// eslint-disable-next-line no-unused-vars
function incdecFilm(filmID, action) {
  let qty = 0;

  const td = findFilmQtyCell(filmID);
  qty = parseInt($(td).text(), 10);

  if (action === 'Increment') {
    qty += 1;
  } else if (action === 'Decrement') {
    qty -= 1;
  }

  const data = {
    data: {
      id: filmID,
      qty,
    },
    action: 'SetQTY',
  };

  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/filmstock/${filmID}`,
    data: JSON.stringify(data),
    contentType: 'application/json',
    dataType: 'json',
    success: updateFilmQty(filmID, qty),
  });
}
