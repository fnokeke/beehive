// '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code)


if (localStorage.gcal_code === "undefined") {
    $("#div-gcal-beehive-connected").hide();
    $("#div-gcal-beehive-success").hide();
    console.log("localStorage.gcal_code is undefined");
} else {
    $("#div-gcal-beehive-connected").show();
    $("#div-gcal-beehive-success").show();
    console.log("localStorage.gcal_code is good");
}

$('#download-gcal-btn').click(function () {
    var start = $('#gcal-start-date').val();
    var end = $('#gcal-end-date').val();

    //alert("start:" + start + "  end:" + end)
    if (start == "" || end == "") {
        alert("Please enter start and end dates");
        return;
    }
    window.location.href = '/gcal/download/{0}/{1}'.format(start, end);
});

$('#btn-save-gcal-code').click(function () {
    var email = $('#gcal_email_from_hidden_element').val();
    var gcalCode = $('#id-gcal-code').val();
    var status = '#gcal-code-status';

    if (gcalCode === '') {
        show_error_msg(status, 'Please provide a valid entry.');
        return;
    }

    var url = 'submit/gcalcode';
    var data = {
        'email': email,
        'code': gcalCode
    };

    $.post(url, data).done(function (resp) {
        resp = JSON.parse(resp);
        console.log('result: ', resp["is_valid"]);
        if (resp['is_valid']) {
            show_success_msg(status, resp['response']);
            localStorage.gcal_code = gcalCode;
            $("#div-gcal-beehive-connected").show();
            $("#div-gcal-beehive-success").show();
            console.log('gcal_code is valid.');

        } else {
            show_error_msg(status, resp['response']);
            localStorage.gcal_code = "undefined";
            $("#div-gcal-beehive-connected").hide();
            $("#div-gcal-beehive-success").hide();
            console.log('gcal_code denied.');
        }
    }).fail(function (error) {
        console.log('error:', error);
        show_error_msg(status, error);
    });

});
