// Make a call to pull all of the user's filmstock
jQuery.ajax({
    type: "GET",
    url: "/api/v1/filmstock",
    contentType: "application/json",
    dataType: "json",
    success: buildStocks
});

/* Helper Functions */
// Find Film Row
function findFilmRow(filmID)
{
  // CSS.escape to add slashes to the colon stuff (was a pain to figure out)
  return "#" + CSS.escape('rowFilm:' + filmID);
}

// Find Film's Qty Table Cell
function findFilmQtyCell(filmID)
{
  return "#" + CSS.escape('film:' + filmID + ':Qty');
}

/* Actions */
// Delete Film
function deleteFilm(filmID)
{
  jQuery.ajax({
    type: "DELETE",
    url: "/api/v1/filmstock/" + filmID,
    contentType: "application/json",
    dataType: "json",
    success: deleteFilmRow(filmID)
  });
}

function deleteFilmRow(filmID)
{
  tr = findFilmRow(filmID);
  $(tr).remove();
}

// Increment/Decrement Film
function incdecFilm(filmID, action)
{
  var qty = 0;

  td = findFilmQtyCell(filmID);
  qty = parseInt($(td).text());

  if(action == 'Increment')
    qty = qty + 1;
  else if(action == 'Decrement')
    qty = qty - 1;

  var data =
  {
      "data" :
      {
        "id": filmID,
        "qty": qty
      },
      "action" : 'SetQTY'
  }

  jQuery.ajax({
    type: "PATCH",
    url: "/api/v1/filmstock/" + filmID,
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: "json",
    success: updateFilmQty(filmID, qty)
  });
}

// Update the film's quantity in the UI
function updateFilmQty(filmID, qty)
{
  td = findFilmQtyCell(filmID);
  $(td).html(qty);
  updateFilmRowColor(filmID, qty);
}

// Update the film's row colors (CSS)
function updateFilmRowColor(filmID, qty)
{
  tr = findFilmRow(filmID);
  $(tr).removeClass();
  if(qty == 0)
    $(tr).addClass('filmStockZero');
  else if(qty < 0)
    $(tr).addClass('filmStockNegative');
}

// Build out the film stocks to produce tables for each film size
function buildStocks(data)
{
  var film35mm = [];
  var filmMediumFormat = [];
  var filmSheets = [];
  var size;

  // Split out film into groups by size
  jQuery(data.data).each(function(i, stock){
    size = stock.size;
    if (size.startsWith("35mm"))
      film35mm.push(stock);
    else if (size == '120' || size == '220')
      filmMediumFormat.push(stock);
    else if (size == '4x5')
      filmSheets.push(stock);
  });

  buildFilmStockTable('35mm', 'film35mm', film35mm);
  buildFilmStockTable('Medium Format', 'filmMediumFormat', filmMediumFormat);
  buildFilmStockTable('Sheets', 'filmSheets', filmSheets);
}

function buildFilmStockTable(title, div, stock)
{
  var filmType;
  var tableID = "table" + div;
  var tableBodyID = "tableBody" + div;

  if(title == 'Sheets')
    filmType = 'Sheets';
  else
    filmType = 'Rolls';

  $('#' + div).append($('<h3>' + title + '</h3>'));
  $('#' + div).append($('<table class="table table-striped table-bordered" id="' + tableID + '"></table>'));
  $('#' + tableID).append($('<thead class="thead-light"><th>Film</th><th>ISO</th><th>Size</th><th>' + filmType + '</th><th></th></thead>'));
  $('#' + tableID).append($('<tbody id="' + tableBodyID + '"></tbody>'));

  jQuery(stock).each(function(i, item){
    var row = '<tr id="rowFilm:' + item.id + '">';
      row += '<td>' + item.brand + ' ' + item.type + '</td>';
      row += '<td>' + item.iso + '</td>';
      row += '<td>' + item.size + '</td>';
      row += '<td id="film:' + item.id + ':Qty">' + item.qty + '</td>';
      row += '<td> \
              <button name="button" value="increment" class="btn btn-sm btn-primary" \
               onclick="incdecFilm(\'' + item.id + '\', \'Increment\')">Increment</button> \
              <button name="button" value="decrement" class="btn btn-sm btn-danger" \
               onclick="incdecFilm(\'' + item.id + '\', \'Decrement\')">Decrement</button> \
              <button type="button" class="btn btn-sm btn-dark" \
               onclick="deleteFilm(\'' + item.id + '\')">Delete</button>';
      row += '</tr>';
    $('#' + tableBodyID).append($(row));
    updateFilmRowColor(item.id, item.qty);
  });
}
