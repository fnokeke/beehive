/*jshint multistr: true */
var naf = (function() {

  var gen_code = $.url_param('gen_code');
  if (gen_code) {
    localStorage.gen_code = gen_code;
  }

  var gen_txt = localStorage.gen_code ? '<strong>' + localStorage.gen_code + '</strong>' : '(<em>no code yet<em/>).';
  $('#naf-gen-code-id').html(gen_txt);
  $('#naf-worker-id').val(localStorage.worker_id);

  $('#naf-submit-btn').click(function(event) {
    event.preventDefault();

    var worker_id = $('#naf-worker-id').val();
    worker_id = worker_id.replace(/[^a-z0-9\s]/gi, '');
    var response_field = '#naf-submit-status';

    if (worker_id === '') {
      show_error_msg(response_field, 'Please submit a valid worker id.');
      return;
    }

    var url = '/naf/enroll/worker_id';
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


  $('#naf-upload-csv-btn').click(function(event) {

    var uploaded_csv = $('#naf-csv-file').get(0).files[0];
    var response_field = "#naf-register-status";
    var form_data = new FormData();
    if (uploaded_csv) {
      console.log('naf-csv-file: ', uploaded_csv);
      form_data.append('naf.csv', uploaded_csv);
    } else {
      show_error_msg(response_field, 'Please upload a valid csv file.');
      return;
    }

    $.ajax({
      url: '/naf/register/csv',
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

  $('#steps-btn').click(function() {
    $('#steps-modal').modal('show');
  });

  $('#naf-read-consent-btn').click(function() {
    $('#naf-consent-agree-modal').modal('show');
  });

  $('#naf-consent-agreed-btn').click(function() {
    $('#naf-consent-agree-modal').modal('hide');
    $('#naf-join-div').show();
    localStorage.agreed_to_consent = "true";
  });

  (function agreed_to_consent() {
    if (localStorage.agreed_to_consent === "true") {
      $('#naf-join-div').show();
    }
  })();

  $('#next-step-btn').click(function() {
    update_steps();
  });

  function update_steps() {
    var current_step = $('#step-value').text();
    var worker_group = parseInt($('#worker-group').text());
    var worker_code = $('#worker-code').text();

    var url = '/naf/update/step';
    var data = {
      'current_step': current_step
    };

    $.post(url, data).done(function(resp) {
      var json_resp = JSON.parse(resp);
      $('#step-value').text(json_resp.next_step);
      $('#btn-step-value').text(get_btn_step_content(json_resp.next_step));
      $('#modal-title-value').html(get_modal_title(json_resp.next_step));
      $('#modal-body-content').html(get_modal_body(json_resp.next_step, worker_group, worker_code));
      check_hide_next_btn(json_resp.next_step);
    }).fail(function(error) {
      console.log('step error: ', error);
    });
  }

  function get_btn_step_content(step) {
    var contents = "Begin Step " + step;
    if (step === 8) {
      contents = "Show mturk code";
    }
    return contents;
  }

  function get_modal_body(step, worker_group, worker_code) {
    var contents = '';
    if (step === 1 || step === 3 || step === 5) {
      contents = get_video(step, worker_group);
    } else if (step === 2 || step === 4 || step === 6) {
      contents = get_survey(step - 1, worker_group);
    } else if (step === 7) {
      contents = get_demography_survey();
    } else if (step === 8) {
      contents = 'Your mturk code: ' + worker_code;
    }
    return contents;
  }

  function get_modal_title(step) {
    var contents = "Step " + step + " of 7";
    if (step === 8) {
      contents = "Submit mturk code";
    }
    return contents;
  }

  function check_hide_next_btn(step) {
    if (step === 8) {
      $('#next-step-btn').hide();
    }
  }

  function get_video(step, worker_group) {
    var order = get_content_order(step, worker_group);
    return get_raw_video(order);
  }

  function get_content_order(step, worker_group) {
    step = parseInt(step);
    worker_group = parseInt(worker_group);
    var video_order = "";
    if (worker_group === 1) {
      video_order = "1,2,3";
    } else if (worker_group === 2) {
      video_order = "1,3,2";
    } else if (worker_group === 3) {
      video_order = "2,1,3";
    } else if (worker_group === 4) {
      video_order = "2,3,1";
    } else if (worker_group === 5) {
      video_order = "3,1,2";
    } else if (worker_group === 6) {
      video_order = "3,2,1";
    }
    video_order = video_order.split(',');

    var order;
    if (step === 1) {
      order = video_order[0];
    } else if (step === 3) {
      order = video_order[1];
    } else if (step === 5) {
      order = video_order[2];
    }
    return parseInt(order);
  }

  function get_raw_video(order) {
    var mp4 = 'v' + order + '.mp4';
    console.log('order: ', order);
    console.log('mp4: ', mp4);

    var raw_html = '<strong>Watch in fullscreen mode and use headphones.</strong>' +
      '<video width="320" height="240" class="vd" id="{0}" controls>'.format(mp4) +
      '<source src="/static/videos/{0}" type="video/mp4">'.format(mp4) +
      'Your browser does not support the video.' +
      '</video>';

    // disable_seeking(mp4);
    return raw_html;
  }

  function get_survey(step, worker_group) {
    var order = get_content_order(step, worker_group);
    var form = '<form>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What was the video about?</label>' +
      '<input type="text" class="form-control" id="formGroupExampleInput" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput2">Rate the video on scale 1(absolutely dislike) - 10(absolutely like).</label>' +
      '<input type="text" class="form-control" id="formGroupExampleInput2" placeholder="Ratings">' +
      '</div>' +
      '</form>';



    var multiStr = "This is the first line \
    	This is the second line \
    	This is more...";


    return form;
  }

  function get_demography_survey() {
    var form = '<form>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">Your Age</label>' +
      '<input type="text" class="form-control" id="formGroupExampleInput" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput2">What part of India are you from?</label>' +
      '<input type="text" class="form-control" id="formGroupExampleInput2" placeholder="type response here.">' +
      '</div>' +
      '</form>';
    return form;
  }

  function init_step_values() {
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    var worker_code = $('#worker-code').text();
    $('#btn-step-value').text(get_btn_step_content(current_step));
    $('#modal-title-value').html(get_modal_title(current_step));
    $('#modal-body-content').html(get_modal_body(current_step, worker_group, worker_code));
    check_hide_next_btn(current_step);
  }
  init_step_values();


  function disable_seeking(video_id) {
    var video = document.getElementById(video_id);
    var supposedCurrentTime = 0;
    video.addEventListener('timeupdate', function() {
      if (!video.seeking) {
        supposedCurrentTime = video.currentTime;
      }
    });
    // prevent user from seeking
    video.addEventListener('seeking', function() {
      // guard agains infinite recursion:
      // user seeks, seeking is fired, currentTime is modified, seeking is fired, current time is modified, ....
      var delta = video.currentTime - supposedCurrentTime;
      if (Math.abs(delta) > 0.01) {
        console.log("Seeking is disabled");
        video.currentTime = supposedCurrentTime;
      }
    });
    // delete the following event handler if rewind is not required
    video.addEventListener('ended', function() {
      // reset state in order to allow for rewind
      supposedCurrentTime = 0;
    });
  }

  $("#v1.mp4").bind("ended", function() {
    alert("video1 has ended");
  });

  $("#v2.mp4").bind("ended", function() {
    alert("video2 has ended");
  });

  $("#v3.mp4").bind("ended", function() {
    alert("video3 has ended");
  });
})();
