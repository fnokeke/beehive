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

  $('#btn-step-begin').click(function() {
    $('#steps-modal').modal('show');
    $('#next-step-btn').prop('disabled', true);

    var current_step = parseInt($('#step-value').text());
    countdown_next_step_btn(current_step);
  });

  $("#steps-modal").on("hidden.bs.modal", function() {
    var vid = $('video').get(0);
    if (vid) {
      vid.pause();
    }
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
    $('#next-step-btn').prop('disabled', true);
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
      $('#span-begin-label').text(get_btn_step_content(json_resp.next_step));
      $('#modal-title-value').html(get_modal_title(json_resp.next_step));
      $('#modal-body-content').html(get_modal_body(json_resp.next_step, worker_group, worker_code));
      countdown_next_step_btn(json_resp.next_step);
    }).fail(function(error) {
      console.log('step error: ', error);
    });
  }

  var g_video_played = false;

  function play_started() {
    g_video_played = true;
    var vid = $('video').attr('id');
    var current_step = parseInt($('#step-value').text());
    countdown_next_step_btn(current_step);
  }

  function countdown_next_step_btn(step) {
    console.log('current step: ', step);
    if (step === 2 || step === 4 || step === 6 || step === 8) {
      g_video_played = false;
    }

    if (step === 1 || step === 3 || step === 5) { // videos
      if (g_video_played) {
        do_countdown(2);
      }
    } else if (step === 2 || step === 4 || step === 6) { // video responses
      do_countdown(2);
    } else if (step === 7) { // demography survey
      do_countdown(2);
    } else if (step === 8) { // final code
      $('#next-step-btn').hide();
    }
  }

  function do_countdown(seconds) {
    setTimeout(function() {
      console.log("next button enabled");
      $('#next-step-btn').prop('disabled', false);
    }, seconds * 1000);
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
    var link;
    if (order === 1) {
      link = "https://www.w3schools.com/html/mov_bbb.mp4";
    } else if (order === 2) {
      link = "https://www.w3schools.com/html/mov_bbb.mp4";
    } else if (order === 3) {
      link = "https://www.w3schools.com/html/mov_bbb.mp4";
    }

    var raw_html = '<strong>Watch in fullscreen mode and use headphones.</strong>' +
      '<video width="320" height="240" id="{0}" onplay="naf.play_started()" controls>' +
      '<source src="{1}" type="video/mp4">'.format(mp4, link) +
      'Your browser does not support the video.' +
      '</video>';

    return raw_html;
  }

  function get_survey(step, worker_group) {
    var order = get_content_order(step, worker_group);
    var form = '<form>' +
      // goes to bottom
      '<div class="form-group">' +
      '<label for="">What was the topic of the video?</label>' +
      '<select class="form-control">' +
      '<option selected>Select response</option>' +
      ' <option value="1">Nutrition of newborn</option>' +
      ' <option value="2">Dangerous effects of smoking and tobacco</option>' +
      ' <option value="3">Importance of washing hands</option>' +
      ' <option value="4">Safe drinking water</option>' +
      ' <option value="5">Treatment of Diarrhea</option>' +
      ' <option value="6">None of these</option>' +
      ' </select>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      '<label for="">Using the image below, indicate how happy or sad you feel after watching the video. Please tick the figure that best represents your feelings. </label>' +
      '<img src="/static/images/naf/valence.png" width="550px" height="150px" alt="valence image" />' +
      '<select class="form-control">' +
      '<option selected>Select response</option>' +
      ' <option value="1">1</option>' +
      ' <option value="2">2</option>' +
      ' <option value="3">3</option>' +
      ' <option value="4">4</option>' +
      ' <option value="5">5</option>' +
      ' </select>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      '<label for="">Using the image below, please indicate how the video affects you. Select the figure that best represents your feelings.</label>' +
      '<img src="/static/images/naf/arousal.png" width="550px" height="100px" alt="arousal image" />' +
      '<select class="form-control">' +
      '<option selected>Select response</option>' +
      ' <option value="1">1</option>' +
      ' <option value="2">2</option>' +
      ' <option value="3">3</option>' +
      ' <option value="4">4</option>' +
      ' <option value="5">5</option>' +
      ' </select>' +
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
      '<label for="formGroupExampleInput">What is your age?</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      // add gender to this: male/female/other
      // what is the highest level of education (make structured)  -- primary / secondary /
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What is your education?</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What is your occupation?</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      // can type a number
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What is your family size?</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      // optional
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What is the occupation of your family members?</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      // in rupees
      '<label for="formGroupExampleInput">What is your monthly family income?</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      // yes - i own one / i share one / i don't have one
      '<label for="formGroupExampleInput">Do you have mobile phones</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      // yes / no
      '<label for="formGroupExampleInput">Do you watch videos on your mobile phones</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      // yes / no
      '<label for="formGroupExampleInput">Do you use Internet on phone?</label>' +
      '<input type="text" class="form-control" id="" placeholder="type response here">' +
      '</div>' +
      '</form>';
    return form;
  }

  function init_step_values() {
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    var worker_code = $('#worker-code').text();
    $('#span-begin-label').text(get_btn_step_content(current_step));
    $('#modal-title-value').html(get_modal_title(current_step));
    $('#modal-body-content').html(get_modal_body(current_step, worker_group, worker_code));
    countdown_next_step_btn(current_step);
  }
  init_step_values();

  var exposed_functions = {
    'play_started': play_started
  };

  return exposed_functions;

})();
