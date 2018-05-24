// '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code)

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
    var email = $('#email_from_hidden_element').val();
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
        } else {
            show_error_msg(status, resp['response']);
            localStorage.gcal_code = undefined;
        }
    }).fail(function (error) {
        console.log('error:', error);
        show_error_msg(status, error);
    });

});
