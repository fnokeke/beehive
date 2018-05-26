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
        'start_date': $('#exp-start-date').val(),
        'end_date': $('#exp-end-date').val(),
        'rescuetime': $('#exp-rescuetime').is(':checked'),
        'calendar': $('#exp-calendar').is(':checked'),
        'phone_notif': $('#exp-phone-notif').is(':checked'),
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
    if (experiment.rescuetime) {
        $('#review-rescuetime-btn').show();
    } else {
        $('#review-rescuetime-btn').hide();
    }

    if (experiment.calendar) {
        $('#review-calendar-btn').show();
    } else {
        $('#review-calendar-btn').hide();
    }

    if (experiment.phone_notif) {
        $('#review-phone-notif-btn').show();
    } else {
        $('#review-phone-notif-btn').hide();
    }

    if (experiment.screen_events) {
        $('#review-screen-events-btn').show();
    } else {
        $('#review-screen-events-btn').hide();
    }

    if (experiment.app_usage) {
        $('#review-app-usage-btn').show();
    } else {
        $('#review-app-usage-btn').hide();
    }

    var data_streams_msg = "#review-data-streams-msg";
    $(data_streams_msg).html('');
    if (!(experiment.rescuetime || experiment.calendar || experiment.phone_notif || experiment.screen_events || experiment.app_usage)) {
        var msg = '<div class="text-center text-primary"> <h5> No Data stream added. </h5></div>';
        $(data_streams_msg).html(msg);
    }

    // Review protocols - show protocols to be added
    redraw_protocols_table('#review-protocols-list-view');
    show_slide(4);
}


//////////////////////////////////////////////////////////
/*######## Function to handle protocol option selection ########*/
//////////////////////////////////////////////////////////

// Function to toggle menu based on Protocol options
$('#protocol-method').on('change', function () {
    console.log('value:', $(this).val());
    if ($(this).val() === "none") {
        $("#div-partial-time-config").addClass("hidden");
        $("#protocol-pam").addClass("hidden");
        $("#protocol-push-notif").addClass("hidden");
        $("#protocol-push-survey").addClass("hidden");
        $("#protocol-vibration-phone-usage").addClass("hidden");
        $("#protocol-vibration-app-usage").addClass("hidden");
    }
    else if ($(this).val() === "push_notification") {
        $("#div-partial-time-config").removeClass("hidden");
        $("#protocol-pam").addClass("hidden");
        $("#protocol-push-notif").removeClass("hidden");
        $("#protocol-push-survey").addClass("hidden");
        $("#protocol-vibration-phone-usage").addClass("hidden");
        $("#protocol-vibration-app-usage").addClass("hidden");
    }
    else if ($(this).val() === "pam") {
        $("#div-partial-time-config").removeClass("hidden");
        $("#protocol-pam").removeClass("hidden");
        $("#protocol-push-survey").addClass("hidden");
        $("#protocol-push-notif").addClass("hidden");
        $("#protocol-vibration-phone-usage").addClass("hidden");
        $("#protocol-vibration-app-usage").addClass("hidden");
    }
    else if ($(this).val() === "push_survey") {
        $("#div-partial-time-config").removeClass("hidden");
        $("#protocol-pam").addClass("hidden");
        $("#protocol-push-survey").removeClass("hidden");
        $("#protocol-push-notif").addClass("hidden");
        $("#protocol-vibration-phone-usage").addClass("hidden");
        $("#protocol-vibration-app-usage").addClass("hidden");
    }
    else if ($(this).val() === "vibration_by_phone_usage") {
        $("#div-partial-time-config").addClass("hidden");
        $("#protocol-pam").addClass("hidden");
        $("#protocol-vibration-phone-usage").removeClass("hidden");
        $("#protocol-push-survey").addClass("hidden");
        $("#protocol-push-notif").addClass("hidden");
        $("#protocol-vibration-app-usage").addClass("hidden");
    }
    else if ($(this).val() === "vibration_by_app_usage") {
        $("#div-partial-time-config").addClass("hidden");
        $("#protocol-pam").addClass("hidden");
        $("#protocol-vibration-app-usage").removeClass("hidden");
        $("#protocol-push-survey").addClass("hidden");
        $("#protocol-push-notif").addClass("hidden");
        $("#protocol-vibration-phone-usage").addClass("hidden");
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

    // Perform data validation
    // start_date = '{0}T00:00:00-05:00'.format(start_date);
    start_date = new Date(start_date);

    // end_date = '{0}T00:00:00-05:00'.format(end_date);
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
        'start_date': $('#exp-start-date').val(),
        'end_date': $('#exp-end-date').val(),
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
function delete_all_protocols() {
    localStorage.setItem("protocols", "[]");
    redraw_protocols_table();
}

function delete_protocol_handler(id) {
    var protocols = localStorage.getItem("protocols");
    protocols = JSON.parse(protocols);
    var result = [];

    for (var i = 0; i < protocols.length; i++) {
        if (id !== protocols[i].id) {
            result.push(protocols[i]);
        }
    }
    result = JSON.stringify(result);
    localStorage.setItem("protocols", result);
    redraw_protocols_table();
}

/*######## Function to handle add new protocol ########*/

// TO DO: Handle create protocol by adding to local storage
function create_protocol_handler() {
    $('#add-protocol-modal').modal('hide');

    // Sorry! No Web Storage support..
    if (typeof(Storage) === "undefined") {
        var msg = "Your browser does not support local storage. Please update your browser or try a different browser.";
        alert(msg);
        return;
    }

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
    var sleep_window_hrs = $('#notification-sleep-time-options').val();
    var sleep_or_awake_mode = $('#protocol-notif-sleep-awake').val();
    var sleep_time = sleep_window_hrs + ';' + sleep_or_awake_mode; // e.g. 2_hour;before_sleep
    var user_window_hrs = $('#notification-user-time-options').val(); // e.g. 3_hour
    var fixed_time = $('#protocol-fixed-exact-time').val(); // e.g. 12:00:00

    var notif_time;
    var notif_type = $('#protocol-options-notif-type').val();
    if (notif_type === 'fixed') {
        notif_time = fixed_time;
    } else if (notif_type === 'user_window') {
        notif_time = user_window_hrs;
    } else if (notif_type === 'sleep_wake') {
        notif_time = sleep_time
    }

    var notif_appid = $('#protocol-notif-appid').val();
    var details;
    var protocol_method = $('#protocol-method').val();
    if (protocol_method === 'none') {
        notif_type = 'none';
        details = '';
    } else if (protocol_method === 'pam') {
        details = 'pam';
    } else if (protocol_method === 'push_survey') {
        details = $('#protocol-survey-details').val();
    } else if (protocol_method === 'push_notification') {
        details = $('#protocol-notif-details').val();
    }

    var protocol = {
        'id': id,
        'label': $('#protocol-label').val(),
        'start_date': $('#protocol-start-date').val(),
        'end_date': $('#protocol-end-date').val(),
        'frequency': $('#protocol-frequency').val(),
        'method': protocol_method,
        'notif_details': details,
        'notif_appid': notif_appid,
        'notif_type': notif_type,
        'notif_time': notif_time,
        'probable_half_notify': $('#probable-half-notify').is(':checked')
    };

    protocols.push(protocol);
    protocols = JSON.stringify(protocols);
    localStorage.setItem("protocols", protocols);

    // Update protocols view
    redraw_protocols_table();
}


/////////////////////////////////////////////////////////
/*######## Functions to display protocols table ########*/

/* Function that updates the protocols view */
function update_protocols_view() {
    var view = create_protocols_table_from_server();
    $('#protocols-list-view').html(view);

}

function beautify_protocol(protocol) {
    console.log('beautify: ', protocol);
    var details = protocol.notif_details.replace(/\n/gi, " / ") + '<br> ~~~~~ <br>';
    if (protocol.method === 'push_notification') {
        details += protocol.notif_appid.replace(/\n/gi, " / ");
    }
    return details;
}

function redraw_protocols_table(viewId) {
    var protocolsViewId = viewId || '#protocols-list-view';
    var protocols = localStorage.getItem("protocols");
    var view = '<div class="text-center text-primary"> ' +
        '<h5> No protocols created. Click on the add protocol button to create a new protocol. </h5>' +
        '</div>';

    if (protocols && (JSON.parse(protocols).length > 0)) {
        protocols = JSON.parse(protocols);
        var isNewStudy = $('#newDivId').data('isnew');
        view = '<table id="protocol-list-table" class="table table-striped table-bordered"><tr>' +
            '<th class="center-text"> Label </th>' +
            '<th class="center-text"> Frequency </th>' +
            '<th class="center-text"> Start Date </th>' +
            '<th class="center-text"> End Date </th>' +
            '<th class="center-text"> Method </th>' +
            '<th class="center-text"> Details </th>' +
            '<th class="center-text"> Half Notify </th>';

        if (isNewStudy) {
            view += '<th class="center-text"> Delete </th>';
        }

        view += '</tr><tbody>';

        // immediately preview protocol to be added
        var details, protocol, row;
        for (var i = protocols.length - 1; i >= 0; i--) {
            protocol = protocols[i];
            details = protocol.notif_details;
            if (protocol.method === 'push_notification' || protocol.method === 'push_survey') {
                details = beautify_protocol(protocol);
            }
            row = '<tr>' +
                '<td class="center-text">' + protocol.label + '</td>' +
                '<td class="center-text">' + protocol.frequency + '</td>' +
                '<td class="center-text">' + formatDate(protocol.start_date) + '</td>' +
                '<td class="center-text">' + formatDate(protocol.end_date) + '</td>' +
                '<td class="center-text">' + protocol.method + '</td>' +
                '<td class="center-text">' + details + '</td>' +
                '<td class="center-text">' + protocol.probable_half_notify + '</td>';

            if (isNewStudy) {
                row += '<td class="center-text">' + '<button class="btn btn-danger btn-sm " onclick="delete_protocol_handler( ' + protocol.id + ' )">';
                row += '<span class="glyphicon glyphicon-remove"></span>' + '</button>' + '</td>' + '</tr>';
            }

            view += row;
        }

        view += '</tbody></table>';
    }

    $(protocolsViewId).html(view);
}

/* Function to populate the protocols table */
function create_protocols_table_from_server() {
    // Create new protocols table
    var server_protocols = $('#slide3').data('protocols');
    if (server_protocols) {
        localStorage.setItem("protocols", JSON.stringify(server_protocols));
    }
    redraw_protocols_table();
}

/*######## Format Date ########*/
function formatDate(rawDate) {
    var parts = rawDate.split('-');
    var date = new Date(parts[0], parts[1] - 1, parts[2]);
    return date.toString().slice(0, 15);
}


function delete_study(code) {
    if (confirm("Are you sure you want to delete this experiment (" + code + ")? This action cannot be reversed.")) {
        window.location.href = '/delete/experiment/{0}'.format(code);
    }
}





