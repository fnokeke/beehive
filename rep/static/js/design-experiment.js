(function(window, document) {

  $('#step1-basic').click(function() {
    show_slide(1);
  });

  $('#step2-data').click(function() {
    show_slide(2);
  });

  $('#step3-protocols').click(function() {
    show_slide(3);
    update_protocols_view();
  });

  $('#step4-approve').click(function() {
    show_slide(4);
  });

  function show_slide(num) {
    $('#slide1').hide();
    $('#slide2').hide();
    $('#slide3').hide();
    $('#slide4').hide();
    $('#slide' + num).show();
  }

})(window, document);


/////////////////////////////////////////////////////////
/*######## Function to handle add new protocol ########*/
function create_protocol_handler() {
// TO DO: Handle create protocol by adding to local storage
    $('#add-protocol-modal').modal('hide');
    alert("Protocol saved")

}

/////////////////////////////////////////////////////////
/*######## Functions to display protocols table ########*/

/* Function that updates the protocols view */
  function update_protocols_view() {
    var view,
      exp,
      row,
      response_field;
    response_field = '#protocols-error-view';

    $.get('/fetch/experiments', function(results) {
      var experiments = JSON.parse(results);
      var view = create_protocols_table(experiments);
      $('#protocols-list-view').html(view);
    }).fail(function(error) {
      show_error_msg(response_field, 'Could not load experiment view.');
      console.warn(error);
    });
  }

 /* Function to populate the protocols table */
  function create_protocols_table(experiments) {
    view = '<table id="exp-list-table" class="table table-striped table-bordered"><tr>' +
      '<th class="center-text"> Title </th>' +
      '<th class="center-text"> Code </th>'  +
      '<th class="center-text"> Start </th>'  +
      '<th class="center-text"> End </th>'  +
      '</tr><tbody>';

    // Add each experiment details to the table
    for (var i = experiments.length - 1; i >= 0; i--) {
      exp = experiments[i];

      row = '<tr>' +
        '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code) +
        '<td class="center-text">' + exp.code + '</td>' +
        '<td class="center-text">' + formatDate(exp.start) + '</td>' +
        '<td class="center-text">' + formatDate(exp.end) + '</td>' +
        '</tr>';

      view += row;
    }

    view += '</tbody></table>';
    return view;
  }

/*######## Format Date ########*/
  function formatDate(rawDate){
    var date = new Date(rawDate);
    date = date.toString().slice(0,15);
    return date;
  }





