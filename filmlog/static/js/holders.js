// Set the holder's state via an API call then call
// function to update HTML
function setHolderState(holderID, action){
  var state = '';
  console.log('setHolderState ' + holderID + ' : ' + action);
  var data =
  {
      "data" :
      {
        "id": holderID
      },
      "action" : action
  }

  switch (action)
  {
    case 'Unload':
      state = 'Empty';
      break;
    case 'Reload':
      state = 'Loaded';
      break;
    case 'Expose':
      state = 'Exposed';
      break;
  }

  jQuery.ajax({
    type: "PATCH",
    url: "/api/v1/holders/" + holderID,
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: "json",
    success: updateHolderState(holderID, state)
  });
}

// Update the holder's state in the UI
function updateHolderState(holderID, state)
{
  var newClass = '';
  switch (state)
  {
    case 'Empty':
      newClass = 'holderEmpty';
      break;
    case 'Loaded':
      newClass = 'holderLoaded';
      break;
    case 'Exposed':
      newClass = 'holderExposed';
      break;
  }

  $('#stateForHolderID' + holderID).removeClass();
  $('#stateForHolderID' + holderID).addClass('holderState');
  $('#stateForHolderID' + holderID).addClass(newClass);
  $('#stateForHolderID' + holderID).html(state);

  updateHolderButtons(holderID, state);
}

// Update the buttons of a holder in the UI
function updateHolderButtons(holderID, state)
{
  loadLocation = "'/gear/holders/" + holderID + "'";
  buttons = ' '
  if(state == 'Loaded')
    buttons += '<button class="btn btn-dark" name="button" value="Expose" \
                onclick="setHolderState(' + holderID + ', \'Expose\')">Expose</button> ';
  if(state == 'Loaded' || state == 'Exposed')
    buttons += '<button class="btn btn-secondary" name="button" value="Unload" \
                onclick="setHolderState(' + holderID + ', \'Unload\')">Unload</button> ';
  if(state == 'Empty')
    buttons += '<button class="btn btn-danger" name="button" value="Load" \
               onclick="location.href=' + loadLocation + '">Load</button> \
               <button class="btn btn-warning" name="button" value="Reload" \
               onclick="setHolderState(' + holderID + ', \'Reload\')">Reload</button> ';

  $('#buttonsForHolderID' + holderID).html(buttons);
}

// Make a call to pull a list of all the user's holders
jQuery.ajax({
    type: "GET",
    url: "/api/v1/holders",
    contentType: "application/json",
    dataType: "json",
    success: function(data)
    {
      jQuery(data.data).each(function(i, holder){
        var row = '<tr id="rowHolderID' + holder.id + '">';
        row += '<td><a href="/gear/holders/' + holder.id + '">' + holder.name + '</a></td>';
        row += '<td>' + holder.size + '</td>';
        row += '<td>' + holder.film + '</td>';
        row += '<td id="stateForHolderID' + holder.id + '">' + holder.state + '</td>';
        row += '<td id="buttonsForHolderID' + holder.id + '"></td></tr>';
        $('#holdersTableBody').append($(row));
        updateHolderState(holder.id, holder.state);
      });
    }
});
