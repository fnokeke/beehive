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


  clean_localStorage();
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
      'screenEvents': $('#exp-screen-events').val(),
      'protocols':{
      },
    };

    // Review basic info
    $('#review-label').val(experiment.label);
    $('#review-title').val(experiment.title);
    $('#review-description').val(experiment.description);
    $('#review-start-date').val(experiment.start);
    $('#review-end-date').val(experiment.end);


    // Review data streams
    var count = 0;
     $('#review-screen-events-btn').hide();
    experiment.screenEvents = $('#exp-screen-events').is(':checked');
    if(experiment.screenEvents){
        count  = count+ 1;
        $('#review-screen-events-btn').show();
        $('#review-screen-events-text').val('ON');
    }

    $('#review-data-streams-msg').html('');
    if(count == 0){
        var msg = '<div class="text-center text-primary"> <h5> No Data stream added. </h5></div>';
        $('#review-data-streams-msg').html(msg);
   }

    $('#review-screen-events').val(experiment.screenEvents);
    console.log("experiment.screenEvents : ", $('#exp-screen-events').is(':checked') );
    console.log("experiment.screenEvents : ", $('#exp-screen-events').val() );

    $('#review-screen-event-btn').hide();
    if(experiment.screenEvents === "on"){
        $('#review-screen-event-btn').show();
    }

    // Review protocols
    protocols = localStorage.getItem("protocols") ;


    if(protocols && (JSON.parse(protocols).length > 0)){
        protocols = JSON.parse(protocols);
        console.log("Protocols length: " , protocols.length);
        var view ;
        view = '<table id="protocol-list-table" class="table table-striped table-bordered"><tr>' +
            '<th class="center-text"> Name </th>' +
            '<th class="center-text"> Frequency </th>'  +
            '<th class="center-text"> Method </th>'  +
            '<th class="center-text"> Start Date </th>'  +
            '<th class="center-text"> End Date </th>'  +
            '<th class="center-text"> Start Time </th>'  +
        '<th class="center-text"> End Time </th>'  +
        '</tr><tbody>';

        // Add each experiment details to the table
        for (var i = protocols.length - 1; i >= 0; i--) {
            protocol = protocols[i];
            row = '<tr>' +
            '<td class="center-text">' + protocol.name + '</td>' +
            '<td class="center-text">' + protocol.frequency + '</td>' +
            '<td class="center-text">' + protocol.method + '</td>' +
            '<td class="center-text">' + formatDate(protocol.startDate) + '</td>' +
            '<td class="center-text">' + formatDate(protocol.endEate) + '</td>' +
            '<td class="center-text">' + protocol.startTime + '</td>' +
            '<td class="center-text">' + protocol.endTime + '</td>' +
            '</tr>';
        view += row;
        }
        view += '</tbody></table>';

    }else{
         view = '<div class="text-center text-primary"> ' +
               '<h5> No protocols created.</h5>' +
               '</div>'
    }

    $('#review-protocols-list-view').html(view);
    show_slide(4);
}


//////////////////////////////////////////////////////////
/*######## Functions to handle add new protocol ########*/
//////////////////////////////////////////////////////////
/*######## Function to clean local storage variables ########*/
function clean_localStorage(){
   if (typeof(Storage) !== "undefined") {
        if(localStorage.getItem("protocols")){
            console.log('protocols[] with length'+ localStorage.getItem("protocols").length +'found.');
            localStorage.removeItem("protocols");
        }else{
            console.log('protocols[] not found.');
        }
   } else {
        // Sorry! No Web Storage support..
        var msg = "Your browser does not support local storage. Please update your browser or try a different browser."
        alert(msg);
   }
}



/*######## Function to delete protocol ########*/
function delete_protocol_handler(id) {
    console.log("deleting protocol" , id);

    var protocols = localStorage.getItem("protocols");
    protocols = JSON.parse(protocols);
    var result=[];
    for (var i = protocols.length - 1; i >= 0; i--) {
        if(id != protocols[i].id){
           result.push( protocols[i] );
        }
    }
    result = JSON.stringify(result);
    localStorage.setItem("protocols", result);
    update_protocols_view();
}

/*######## Function to handle add new protocol ########*/
function create_protocol_handler() {
// TO DO: Handle create protocol by adding to local storage
    $('#add-protocol-modal').modal('hide');

    if (typeof(Storage) !== "undefined") {
        var protocols = [];
        var id = 0;
        if(localStorage.getItem("protocols")){
            console.log('protocols[] with length'+ localStorage.getItem("protocols").length +'  found.');
            protocols = localStorage.getItem("protocols");
            // Convert JSON to object
            protocols = JSON.parse(protocols);
            console.log('protocols[] array found of length: ' + protocols.length );
            if(protocols.length>0){
                var max=0;
                    for (var i = protocols.length - 1; i >= 0; i--) {
                        if(protocols[i].id > max){
                            max = protocols[i].id;
                        }
                    }
                id = max + 1;
            }

            console.log( "Next id; " , id );
            console.log( "All elemenst in protocols; " , protocols );

        }else{
            console.log('protocols[] not found.');
        }

        // Create protocol objects
        var protocol = {
                'id':id,
                'name' :$('#protocol-name').val(),
                'frequency' :$('#protocol-frequency').val(),
                'method' :$('#protocol-method').val(),
                'startDate' :$('#protocol-start-date').val(),
                'endDate' :$('#protocol-end-date').val(),
                'startTime' :$('#protocol-start-time').val(),
                'endTime' :$('#protocol-end-time').val(),
            };

        protocols.push(protocol);
        protocols = JSON.stringify(protocols);
        localStorage.setItem("protocols", protocols);

        // Code for localStorage/sessionStorage.
        // Store
        // localStorage.setItem("title", protocol);
        // localStorage.setItem("protocols", protocol);
        // Retrieve
        // var local = localStorage.getItem("title");
        // remove
        // localStorage.removeItem("title");

        /*
        console.log("Num storage:" + localStorage.length);
        for(var i=0, len=localStorage.length; i<len; i++) {
            var key = localStorage.key(i);
            var value = localStorage[key];
            console.log(key + " => " + value);
        }
        */

    } else {
        // Sorry! No Web Storage support..
        var msg = "Your browser does not support local storage. Please update your browser or try a different browser."
        alert(msg);
    }

    // Update protocols view
    update_protocols_view();
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

    // TO DO : Extract data from local storage and display protocols
    protocols = localStorage.getItem("protocols");
  }

 /* Function to populate the protocols table */
  function create_protocols_table(experiments) {

   // ####################################################
   // Create protocols table
    var protocols = localStorage.getItem("protocols");
    var view;

    if (protocols && (JSON.parse(protocols).length > 0)) {
        protocols = JSON.parse(protocols);
        console.log(' Parse protocols length :' , protocols.length);
        console.log(' Parse protocols object :' , protocols);

        view = '<table id="protocol-list-table" class="table table-striped table-bordered"><tr>' +
            '<th class="center-text"> Id </th>' +
            '<th class="center-text"> Name </th>' +
            '<th class="center-text"> Frequency </th>'  +
            '<th class="center-text"> Method </th>'  +
            '<th class="center-text"> Start Date </th>'  +
            '<th class="center-text"> End Date </th>'  +
            '<th class="center-text"> Start Time </th>'  +
            '<th class="center-text"> End Time </th>'  +
            '<th class="center-text"> Delete </th>' +
            '</tr><tbody>';

        // Add each experiment details to the table
        for (var i = protocols.length - 1; i >= 0; i--) {
            protocol = protocols[i];
            row = '<tr>' +
                '<td class="center-text">' + protocol.id + '</td>' +
                '<td class="center-text">' + protocol.name + '</td>' +
                '<td class="center-text">' + protocol.frequency + '</td>' +
                '<td class="center-text">' + protocol.method + '</td>' +
                '<td class="center-text">' + formatDate(protocol.startDate) + '</td>' +
                '<td class="center-text">' + formatDate(protocol.endDate) + '</td>' +
                '<td class="center-text">' + protocol.startTime + '</td>' +
                '<td class="center-text">' + protocol.endTime + '</td>' +
                '<td class="center-text">' + '<button class="btn btn-danger btn-sm " onclick="delete_protocol_handler( '+ protocol.id +' )">' +
                    '<span class="glyphicon glyphicon-remove"></span>' + '</button>' + '</td>' +
                '</tr>';

            view += row;
        }

        view += '</tbody></table>';
        return view;
    } else {
        view = '<div class="text-center text-primary"> ' +
               '<h5> No protocols created. Click on the add protocol button to create a new protocol. </h5>' +
               '</div>'
        return view;
    }

   // ####################################################
   // Create experiments table
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





