const searchParams = new URLSearchParams(window.location.search);
const printView = searchParams.get('print');

// Update the buttons of a holder in the UI
function updateHolderButtons(holderID, state) {
  const loadLocation = `/gear/holders/${holderID}`;
  let buttons = ' ';
  if (state === 'Loaded') {
    buttons += `<button class="btn btn-sm btn-dark" name="button" value="Expose" \
                onclick="setHolderState('${holderID}', 'Expose')">Expose</button> `;
  }
  if (state === 'Loaded' || state === 'Exposed') {
    buttons += `<button class="btn btn-sm btn-secondary" name="button" value="Unload" \
                onclick="setHolderState('${holderID}', 'Unload')">Unload</button>`;
  }
  if (state === 'Empty') {
    buttons += `<button class="btn btn-sm btn-danger" name="button" value="Load" \
               onclick="location.href='${loadLocation}'">Load</button> \
               <button class="btn btn-sm btn-warning" name="button" value="Reload" \
               onclick="setHolderState('${holderID}', 'Reload')">Reload</button>`;
  }
  $(`#buttonsForHolderID${holderID}`).html(buttons);
}

// Update the holder's state in the UI
function updateHolderState(holderID, state) {
  let newClass = '';
  switch (state) {
    case 'Empty':
      newClass = 'holderEmpty';
      break;
    case 'Loaded':
      newClass = 'holderLoaded';
      break;
    case 'Exposed':
      newClass = 'holderExposed';
      break;
    default:
      newClass = 'Unknown';
  }

  $(`#stateForHolderID${holderID}`).removeClass();
  $(`#stateForHolderID${holderID}`).addClass('holderState');
  $(`#stateForHolderID${holderID}`).addClass(newClass);
  $(`#stateForHolderID${holderID}`).html(state);

  updateHolderButtons(holderID, state);
}

// Set the holder's state via an API call then call
// function to update HTML
// eslint-disable-next-line no-unused-vars
function setHolderState(holderID, action) {
  let state = '';
  const data = {
    data: {
      id: holderID,
    },
    action,
  };

  switch (action) {
    case 'Unload':
      state = 'Empty';
      break;
    case 'Reload':
      state = 'Loaded';
      break;
    case 'Expose':
      state = 'Exposed';
      break;
    default:
      state = 'Unknown';
  }

  jQuery.ajax({
    type: 'PATCH',
    url: `/api/v1/holders/${holderID}`,
    data: JSON.stringify(data),
    contentType: 'application/json',
    dataType: 'json',
    success: updateHolderState(holderID, state),
  });
}

// Make a call to pull a list of all the user's holders
function getHolders() {
  $('#holdersTableBody').empty();
  jQuery.ajax({
    type: 'GET',
    url: '/api/v1/holders',
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      jQuery(data.data).each((i, holder) => {
        let film = '';
        if (holder.film) {
          ({ film } = holder);
        }
        let row = `<tr id="rowHolderID${holder.id}">`;
        row += `<td><a href="/gear/holders/${holder.id}">${holder.name}</a></td>`;
        row += `<td>${holder.size}</td>`;
        row += `<td>${film}</td>`;
        row += `<td id="stateForHolderID${holder.id}">${holder.state}</td>`;
        if (!printView) {
          row += `<td id="buttonsForHolderID${holder.id}"></td></tr>`;
        }
        $('#holdersTableBody').append($(row));
        updateHolderState(holder.id, holder.state);
      });
    },
  });
}

function addHolder() {
  const holder = {
    data: {
      name: $('#holderName').val(),
      size: $('#holderSize').val(),
      notes: $('#holderNotes').val(),
    },
  };

  // Form validation
  if (!$('#holderName').val()) {
    showAlert('Cannot Add Holder', 'It needs a name', 'danger');
    return;
  }

  jQuery.ajax({
    type: 'POST',
    url: '/api/v1/holders',
    data: JSON.stringify(holder),
    contentType: 'application/json',
    dataType: 'json',
    success(data) {
      // We re-generate the table so it sorts properly
      getHolders(data.data);
      $('#holderForm')[0].reset();
    },
    statusCode: { 409() { showAlert('Cannot Add Holder', 'It already exists', 'danger'); } },
  });
}

$(document).ready(() => { getHolders(); });

// Add Holder on form submission
$('form').on('submit', (e) => {
  e.preventDefault();
  addHolder();
});
