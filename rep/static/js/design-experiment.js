(function(window, document) {

  $('#exp-start-date').datepicker('setDate', new Date());
  $('#exp-end-date').datepicker('setDate', new Date());

  $('#step1-basic').click(function() {
    show_slide(1);
  });

  $('#step2-data').click(function() {
    show_slide(2);
  });

  $('#step3-protocols').click(function() {
    update_protocols_view();
    show_slide(3);
  });

  $('#step4-preview').click(function() {
    // load preview state variables
    show_slide(4);
  });

//  function show_slide(num) {
//    $('#slide1').hide();
//    $('#slide2').hide();
//    $('#slide3').hide();
//    $('#slide4').hide();
//    $('#slide' + num).show();
//  }

  load_slide1();
})(window, document);


/////////////////////////////////////////////////////////
/*######## Next handlers for design experiment ########*/
function show_slide(num) {
    $('#slide1').hide();
    $('#slide2').hide();
    $('#slide3').hide();
    $('#slide4').hide();
    $('#slide' + num).show();
  }

function load_slide1(){
    // TO DO: Slide1 validations
    show_slide(1);
}

function load_slide2(){
    // TO DO: Slide1 validations
    show_slide(2);
}

function load_slide3(){
    // TO DO: Slide2 validations
    update_protocols_view();
    show_slide(3);
}

function load_slide4(){
    // TO DO: all validations

      var experiment = {
      'label': $('#exp-label').val(),
      'title': $('#exp-title').val(),
      'description': $('#exp-title').val(),
      'start': $('#exp-end-date').val(),
      'end': $('#exp-end-date').val(),
      'screen-events': '',
      'protocols':{
      },
    };

    // Show data for review
    $('#review-label').val(experiment.label);
    $('#review-title').val(experiment.title);
    $('#review-description').val(experiment.description);
    $('#review-start-date').val(experiment.start);
    $('#review-end-date').val(experiment.end);
    show_slide(4);
}


/////////////////////////////////////////////////////////
/*######## Function to handle add new protocol ########*/
function create_protocol_handler() {
// TO DO: Handle create protocol by adding to local storage
    $('#add-protocol-modal').modal('hide');

    if (typeof(Storage) !== "undefined") {
        // Code for localStorage/sessionStorage.
        // Store
        localStorage.setItem("title", "Smith");
        // Retrieve
        var local = localStorage.getItem("title");
        alert("Saved to storage " + local);
    } else {
        // Sorry! No Web Storage support..
        var msg = "Your browser does not support local storage. Please update your browser or try a different browser."
        alert(msg);
    }
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





