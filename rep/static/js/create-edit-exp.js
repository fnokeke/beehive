(function (window, document) {

    // $('#exp-start-date').datepicker('setDate', new Date());
    // $('#exp-end-date').datepicker('setDate', new Date());

    $('#step1-basic').click(function () {
        focus_slide1();
        show_slide(1);
    });

    $('#step2-data').click(function () {
        focus_slide2();
        show_slide(2);
    });

    $('#step3-protocols').click(function () {
        focus_slide3();
        update_protocols_view();
        show_slide(3);
    });

    $('#step4-preview').click(function () {
        // load preview state variables
        focus_slide4();
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


function focus_slide1() {
    $("#step2-data").removeClass("btn-info");
    $("#step3-protocols").removeClass("btn-info");
    $("#step4-preview").removeClass("btn-info");
    $("#step1-basic").addClass("btn-info");
}

function focus_slide2() {
    $("#step1-basic").removeClass("btn-info");
    $("#step3-protocols").removeClass("btn-info");
    $("#step4-preview").removeClass("btn-info");
    $("#step2-data").addClass("btn-info");
}

function focus_slide3() {
    $("#step1-basic").removeClass("btn-info");
    $("#step2-data").removeClass("btn-info");
    $("#step4-preview").removeClass("btn-info");
    $("#step3-protocols").addClass("btn-info");
}

function focus_slide4() {
    $("#step1-basic").removeClass("btn-info");
    $("#step2-data").removeClass("btn-info");
    $("#step3-protocols").removeClass("btn-info");
    $("#step4-preview").addClass("btn-info");
}


/////////////////////////////////////////////////////////
/*######## Next handlers for design experiment ########*/
function show_slide(num) {
    $('#slide1').hide();
    $('#slide2').hide();
    $('#slide3').hide();
    $('#slide4').hide();
    $('#slide5').hide();
    $('#slide' + num).show();
}

function load_slide1() {
    // TO DO: Slide1 validations
    focus_slide1();
    show_slide(1);
}

function load_slide2() {
    // TO DO: Slide1 validations
    focus_slide2();
    show_slide(2);
}

function load_slide3() {
    // TO DO: Slide2 validations
    focus_slide3();
    update_protocols_view();
    show_slide(3);
}

function load_slide4() {
    // TO DO: all validations
    focus_slide4();

    //clear errors
    $('#review-experiment-error').html('');

    var experiment = {
        'label': $('#exp-label').val(),
        'title': $('#exp-title').val(),
        'description': $('#exp-description').val(),
        'start_date': $('#exp-end-date').val(),
        'end_date': $('#exp-end-date').val(),
        'screen_events': $('#exp-screen-events').is(':checked'),
        'app_usage': $('#exp-app-usage').is(':checked'),
        'protocols': {}
    };

    // Review basic info
    $('#review-label').val(experiment.label);
    $('#review-title').val(experiment.title);
    $('#review-description').val(experiment.description);
    $('#review-start-date').val(experiment.start_date);
    $('#review-end-date').val(experiment.end_date);


    // Review data streams
    var count = 0;
    $('#review-screen-events-btn').hide();
    $('#review-app-usage-btn').hide();

    experiment.screenEvents = $('#exp-screen-events').is(':checked');
    if (experiment.screenEvents) {
        count = count + 1;
        $('#review-screen-events-btn').show();
    }

    experiment.appUsage = $('#exp-app-usage').is(':checked');
    if (experiment.appUsage) {
        count = count + 1;
        $('#review-app-usage-btn').show();
    }

    $('#review-data-streams-msg').html('');
    if (count == 0) {
        var msg = '<div class="text-center text-primary"> <h5> No Data stream added. </h5></div>';
        $('#review-data-streams-msg').html(msg);
    }

    $('#review-screen-events').val(experiment.screenEvents);

    $('#review-screen-event-btn').hide();
    if (experiment.screenEvents === "on") {
        $('#review-screen-event-btn').show();
    }

    // Review protocols
    protocols = localStorage.getItem("protocols");


    if (protocols && (JSON.parse(protocols).length > 0)) {
        protocols = JSON.parse(protocols);
        var view;
        view = '<table id="protocol-list-table" class="table table-striped table-bordered"><tr>' +
            '<th class="center-text"> Label </th>' +
            '<th class="center-text"> Frequency </th>' +
            '<th class="center-text"> Method </th>' +
            '<th class="center-text"> Start Date </th>' +
            '<th class="center-text"> End Date </th>' +
            '<th class="center-text"> Notification </th>' +
            '<th class="center-text"> Half Notify </th>' +
            '</tr><tbody>';

        // Add each experiment details to the table
        var notif, protocol, row;
        for (var i = protocols.length - 1; i >= 0; i--) {
            protocol = protocols[i];
            notif = 'n/a';
            if (protocol.method === 'push_notification') {
                notif = protocol.notif_title + ' / ' + protocol.notif_content + ' / ' + protocol.notif_appid;
            }
            row = '<tr>' +
                '<td class="center-text">' + protocol.label + '</td>' +
                '<td class="center-text">' + protocol.frequency + '</td>' +
                '<td class="center-text">' + protocol.method + '</td>' +
                '<td class="center-text">' + formatDate(protocol.start_date) + '</td>' +
                '<td class="center-text">' + formatDate(protocol.end_date) + '</td>' +
                '<td class="center-text">' + notif + '</td>' +
                '<td class="center-text">' + protocol.probable_half_notify + '</td>' +
                '</tr>';
            view += row;
        }
        view += '</tbody></table>';

    } else {
        view = '<div class="text-center text-primary"> ' +
            '<h5> No protocols created.</h5>' +
            '</div>'
    }

    $('#review-protocols-list-view').html(view);
    show_slide(4);
}


//////////////////////////////////////////////////////////
/*######## Function to handle protocol option selection ########*/
//////////////////////////////////////////////////////////

// Function to toggle menu based on Protocol options
$('#protocol-method').on('change', function () {
    console.log('value:', $(this).val());
    if ($(this).val() === "none") {
        $("#protocol-date-time").addClass("hidden");
        $("#notification-types").addClass("hidden");
    }
    else if ($(this).val() === "push_notification") {
        $("#protocol-date-time").addClass("hidden");
        $("#notification-types").removeClass("hidden");
    }
    else {
        $("#protocol-date-time").removeClass("hidden");
        $("#notification-types").addClass("hidden");
    }
});


// Function to toggle menu based on Notification options
$('#protocol-options-notif-type').on('change', function () {
    if ($(this).val() === "fixed") {
        $("#div-notif-fixed").removeClass("hidden");
        $("#div-notif-user-window").addClass("hidden");
        $("#div-notif-sleep-awake").addClass("hidden");
    }
    else if ($(this).val() === "user_window") {
        $("#div-notif-fixed").addClass("hidden");
        $("#div-notif-user-window").removeClass("hidden");
        $("#div-notif-sleep-awake").addClass("hidden");
    }
    else {
        $("#div-notif-fixed").addClass("hidden");
        $("#div-notif-user-window").addClass("hidden");
        $("#div-notif-sleep-awake").removeClass("hidden");
    }
});

// Function to handle notification-fixed-random checkbox
$('#notification-fixed-random').click(function () {
    if ($(this).is(':checked')) {
        $("#notification-fixed-time").prop("disabled", true);
    } else {
        $("#notification-fixed-time").prop("disabled", false);
    }
});


// Function to handle notification-user-random checkbox
// $('#probable-half-notify').click(function () {
//     console.log($(this).is(':checked'));
//     if ($(this).is(':checked')) {
//         $("#notification-user-time-options").prop("disabled", true);
//     } else {
//         $("#notification-user-time-options").prop("disabled", false);
//     }
// });


//////////////////////////////////////////////////////////
/*######## Function to create in experiment in database ########*/

//////////////////////////////////////////////////////////

function create_experiment_handler() {
    // Clean up data and call server api
    var response_field = '#review-experiment-error';

    var owner = $('#exp-owner').val();
    var label = $('#exp-label').val();
    var title = $('#exp-title').val();
    var description = $('#exp-description').val();
    var start_date = $('#exp-start-date').val();
    var end_date = $('#exp-end-date').val();
    var screen_events = $('#exp-screen-events').is(':checked');
    var app_usage = $('#exp-app-usage').is(':checked');
    var protocols = localStorage.getItem("protocols");

    // Perform data validation
    start_date = '{0}T00:00:00-05:00'.format(start_date);
    start_date = new Date(start_date);

    end_date = '{0}T00:00:00-05:00'.format(end_date);
    end_date = new Date(end_date);

    if (start_date.getTime() > end_date.getTime()) {
        show_error_msg(response_field, 'Start date must come before end date.');
        return;
    }

    var url = '/add/experiment/v2';
    var data = {
        'label': label,
        'title': title,
        'description': description,
        'start_date': start_date.toJSON(),
        'end_date': end_date.toJSON(),
        'screen_events': screen_events,
        'app_usage': app_usage,
        'protocols': localStorage.protocols || '[]',
        'owner': owner,
        'probable_half_notify': $('#probable-half-notify').is(':checked')
    };

    // Hide button on click to avoid multiple requests
    $('#create_experiment_btn').hide();

    $.post(url, data).done(function (resp) {
        var msg = '<div class="text-center text-success"> <h4> Data Submitted  Successfully </h4></div>';
        $('#review-experiment-success').html(msg);
        $('#create_experiment_btn').hide();
        show_slide(5);

        setTimeout(function () {
            window.location.href = window.location.origin + "/experiments";
        }, 1500);

    }).fail(function (response) {
        $('#create_experiment_btn').show();
        response_field = '#review-experiment-error';
        show_error_msg(response_field, response.responseText);
    });
}

//
//function on_success_handler(){
//    console.log("Submission on_success_handler");
//    window.location.href = window.location.origin;
//}


//////////////////////////////////////////////////////////
/*######## Functions to handle add new protocol ########*/
//////////////////////////////////////////////////////////
/*######## Function to clean local storage variables ########*/
function clean_localStorage() {
    if (typeof(Storage) !== "undefined") {
        if (localStorage.getItem("protocols")) {
            localStorage.removeItem("protocols");
        }
    } else {
        // Sorry! No Web Storage support..
        var msg = "Your browser does not support local storage. Please update your browser or try a different browser."
        alert(msg);
    }
}

/*######## Function to delete protocol ########*/
function delete_protocol_handler(id) {
    var protocols = localStorage.getItem("protocols");
    protocols = JSON.parse(protocols);
    var result = [];

    for (var i = 0; i < protocols.length; i++) {
        if (id != protocols[i].id) {
            result.push(protocols[i]);
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
        if (localStorage.getItem("protocols")) {
            protocols = localStorage.getItem("protocols");
            // Convert JSON to object
            protocols = JSON.parse(protocols);
            if (protocols.length > 0) {
                var max = 0;
                for (var i = protocols.length - 1; i >= 0; i--) {
                    if (protocols[i].id > max) {
                        max = protocols[i].id;
                    }
                }
                id = max + 1;
            }
        }

        // Create protocol objects
        var notif_type = $('#protocol-options-notif-type').val();
        var sleep_window_hrs = $('#notification-sleep-time-options').val();
        var sleep_or_awake_mode = $('#protocol-notif-sleep-awake').val();
        var sleep_time = sleep_window_hrs + ';' + sleep_or_awake_mode; // e.g. 2_hour;before_sleep
        var user_window_hrs = $('#notification-user-time-options').val(); // e.g. 3_hour
        var fixed_time = $('#protocol-fixed-exact-time').val(); // e.g. 12:00:00

        var notif_time = 'n/a';
        if (notif_type === 'fixed') {
            notif_time = fixed_time;
        } else if (notif_type === 'user_window') {
            notif_time = user_window_hrs;
        } else if (notif_type === 'sleep_wake') {
           notif_time = sleep_time
        }

        var protocol = {
            'id': id,
            'label': $('#protocol-label').val(),
            'method': $('#protocol-method').val(),
            'start_date': $('#protocol-start-date').val(),
            'end_date': $('#protocol-end-date').val(),
            'frequency': $('#protocol-frequency').val(),
            'notif_title': $('#protocol-notif-title').val(),
            'notif_content': $('#protocol-notif-content').val(),
            'notif_appid': $('#protocol-notif-appid').val(),
            'notif_type': notif_type,
            'notif_time': notif_time,
            'probable_half_notify': $('#probable-half-notify').is(':checked')
        };

        protocols.push(protocol);
        protocols = JSON.stringify(protocols);
        localStorage.setItem("protocols", protocols);

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

    $.get('/fetch/experiments', function (results) {
        var experiments = JSON.parse(results);
        var view = create_protocols_table(experiments);
        $('#protocols-list-view').html(view);
    }).fail(function (error) {
        show_error_msg(response_field, 'Could not load experiment view.');
        console.warn(error);
    });

    // TO DO : Extract data from local storage and display protocols
    var protocols = localStorage.getItem("protocols");
}

/* Function to populate the protocols table */
function create_protocols_table(experiments) {

    // ####################################################
    // Create protocols table
    var protocols = localStorage.getItem("protocols");
    var view;

    if (protocols && (JSON.parse(protocols).length > 0)) {
        protocols = JSON.parse(protocols);
        view = '<table id="protocol-list-table" class="table table-striped table-bordered"><tr>' +
            '<th class="center-text"> Label </th>' +
            '<th class="center-text"> Frequency </th>' +
            '<th class="center-text"> Method </th>' +
            '<th class="center-text"> Start Date </th>' +
            '<th class="center-text"> End Date </th>' +
            '<th class="center-text"> Notification </th>' +
            '<th class="center-text"> Half Notify </th>' +
            '<th class="center-text"> Delete </th>' +
            '</tr><tbody>';

        // Add each experiment details to the table
        var notif, protocol, row;
        for (var i = protocols.length - 1; i >= 0; i--) {
            protocol = protocols[i];
            notif = 'n/a';
            //TODO: refactor this repeating code
            if (protocol.method === 'push_notification') {
                notif = protocol.notif_title + ' / ' + protocol.notif_content + ' / ' + protocol.notif_appid;
            }
            row = '<tr>' +
                '<td class="center-text">' + protocol.label + '</td>' +
                '<td class="center-text">' + protocol.frequency + '</td>' +
                '<td class="center-text">' + protocol.method + '</td>' +
                '<td class="center-text">' + formatDate(protocol.start_date) + '</td>' +
                '<td class="center-text">' + formatDate(protocol.end_date) + '</td>' +
                '<td class="center-text">' + notif + '</td>' +
                '<td class="center-text">' + protocol.probable_half_notify + '</td>' +
                '<td class="center-text">' + '<button class="btn btn-danger btn-sm " onclick="delete_protocol_handler( ' + protocol.id + ' )">' +
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
        '<th class="center-text"> Code </th>' +
        '<th class="center-text"> Start </th>' +
        '<th class="center-text"> End </th>' +
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
function formatDate(rawDate) {
    var date = new Date(rawDate);
    date = date.toString().slice(0, 15);
    return date;
}





