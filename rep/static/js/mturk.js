(function(window, document, $) {

  var gen_code = $.url_param('gen_code');
  if (gen_code) {
    localStorage.gen_code = gen_code;
  }

  var gen_txt = localStorage.gen_code ? '<strong>' + localStorage.gen_code + '</strong>' : '(<em>no code yet<em/>).';
  $('#gen-code-id').html(gen_txt);
  $('#mturk-worker-id').val(localStorage.worker_id);

  $('#mturk-submit-btn').click(function(event) {
    event.preventDefault();

    var worker_id = $('#mturk-worker-id').val();
    worker_id = worker_id.replace(/[^a-z0-9\s]/gi, '');
    var response_field = '#mturk-submit-status';

    if (worker_id === '') {
      show_error_msg(response_field, 'Please submit a valid worker id.');
      return;
    }

    var url = '/mturk/verify/worker_id';
    var data = {
      'worker_id': worker_id
    };

    $.post(url, data).done(function(resp) {
      localStorage.worker_id = worker_id;

      if (resp.indexOf("cannot") > -1) {
        show_error_msg(response_field, resp);
      } else {
        show_success_msg(response_field, resp);
      }

    }).fail(function(error) {
      var msg = 'Submission error. Please contact MTurk Requester (Error: {0} / {1}).'.format(error.status, error.statusText);
      show_error_msg(response_field, msg);
    });

  });


  $('#mturk-upload-csv-btn').click(function(event) {

    var uploaded_csv = $('#mturk-csv-file').get(0).files[0];
    var response_field = "#mturk-register-status";
    var form_data = new FormData();
    if (uploaded_csv) {
      console.log('mturk-csv-file: ', uploaded_csv);
      form_data.append('mturk.csv', uploaded_csv);
    } else {
      show_error_msg(response_field, 'Please upload a valid csv file.');
      return;
    }

    $.ajax({
      url: '/mturk/register/csv',
      success: function(resp) {

        if (resp === -1) {
          show_error_msg(response_field, 'Error receiving uploaded file');
        } else {
          show_success_msg(response_field, resp);
        }

      },
      error: function(e) {
        show_error_msg(response_field, 'Upload error. Pls contact researcher. ' + e.statusText);
      },
      complete: function(e) {
        setTimeout(function() {
          // show_plain_msg(response_field, '');
          // window.location.href = window.location.href;
        }, 1500);
      },
      data: form_data,
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false
    });
    return false;

  });


})(window, document, jQuery);
