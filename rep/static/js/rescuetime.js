
$('#select-days').change(function() {
    var days = $('#select-days').val()
    window.location.href = '/rescuetime/stats?days={0}'.format(days );
});

$('#btn-save-rtime-code').click(function () {
    var email = $('#rtime_email_from_hidden_element').val();
    var rtimeCode = $('#id-rtime-code').val();
    var status = '#rtime-code-status';

    if (rtimeCode === '') {
        show_error_msg(status, 'Please provide a valid entry.');
        return;
    }

    var url = 'submit/rtime-code';
    var data = {
        'email': email,
        'code': rtimeCode
    };

    $.post(url, data).done(function (resp) {
        resp = JSON.parse(resp);
        console.log('result: ', resp["is_valid"]);
        if (resp['is_valid']) {
            show_success_msg(status, resp['response']);
            localStorage.gcal_code = rtimeCode;
        } else {
            show_error_msg(status, resp['response']);
            localStorage.gcal_code = undefined;
        }
    }).fail(function (error) {
        console.log('error:', error);
        show_error_msg(status, error);
    });

});
