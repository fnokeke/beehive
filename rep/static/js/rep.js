////////////////////////////////////////////////
// rep.js
////////////////////////////////////////////////

// add date range values for experiment start and end dates
$('.input-daterange input').each(function () {
    $(this).datepicker('clearDates');
});

////////////////////////////////////////////////
// helper functions
////////////////////////////////////////////////

function show_busy_div(div) {
    $(div).html('Processing...').css('color', 'orange');
}

function submit_checkbox_val(field, input) {
    var url = 'settings/tracking/' + field + '/' + input;
    var response_field = '#' + field + '-checkbox-status';

    $.get(url, function (resp) {
        var results = JSON.parse(resp);
        console.log('results: ', results);
    }).fail(function (error) {
        console.log('error:', error);
        show_error_msg(response_field, error);
    });
}

////////////////////////////////////////////////
// authenticate/connect data streams
////////////////////////////////////////////////
$('#signin-btn').click(function () {
    window.location.href = '/google_login';
});

$('#mturk-auth-moves-btn').click(function () {

    if ($('#mturk-worker-id').val() === '') {
        show_error_msg('#mturk-submit-status', 'Submit a valid worker id before you connect Moves app.');
        return;
    }
    window.location.href = '/mturk-auth-moves';
});

$('#auth-moves-btn').click(function () {
    $('#auth-status-div').html('connecting to moves...');
    window.location.href = '/auth-moves';
});

$('#auth-omh-btn').click(function () {
    window.location.href = '/auth-omh';
});

$('#auth-rt-btn').click(function () {
    window.location.href = '/auth-rt';
});


// #################################################
// update profile fields
// #################################################
$('#update-profile-btn').click(function () {
    var firstname = $('#firstname-field').val();
    var lastname = $('#lastname-field').val();
    var gender = $('#gender-field').val();
    var data;
    var url = 'settings/profile/update';

    if (firstname === '' && lastname === '' && gender === '') {
        show_error_msg('#update-profile-status', 'You cannot have all fields empty.');
        return;
    }

    data = {
        'firstname': firstname,
        'lastname': lastname,
        'gender': gender
    };

    $.post(url, data).done(function (resp) {
        show_success_msg('#update-profile-status', 'profile successfully updated');
    }).fail(function (error) {
        console.log('error:', error);
        show_error_msg('#update-profile-status', error);
    });

});

// #################################################
// page animation for message
// #################################################
$(".alert-dismissible").each(function (index) {
    var $me = $(this);
    $me.delay(2000 + 800 * index).fadeTo(200, 0).slideUp(200, function () {
        $me.alert('close');
    });
});

