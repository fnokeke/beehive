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
    $('#step-value').text(1);
    console.log('step reset to 1');
    init_step_values();
    localStorage.clear();
    localStorage.agreed_to_consent = "true";

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
      $('#next-step-btn').prop('disabled', true);
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
    $('#next-step-btn').prop('disabled', true);

    console.log('current step: ', step);
    if (step === 2 || step === 4 || step === 6 || step === 8) {
      g_video_played = false;
    }

    if (g_video_played && (step === 1 || step === 3 || step === 5)) { // videos
      do_countdown(65);
    }

    // survey1 completed
    if (step === 2 && localStorage.v1q1 !== "undefined" && localStorage.v1q2 !== "undefined" && localStorage.v1q3 !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
    }

    // survey2 completed
    if (step === 4 && localStorage.v2q1 !== "undefined" && localStorage.v2q2 !== "undefined" && localStorage.v2q3 !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
    }

    // survey3 completed
    if (step === 6 && localStorage.v3q1 !== "undefined" && localStorage.v3q2 !== "undefined" && localStorage.v3q3 !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
    }

    // demography survey completed
    if (step === 7 &&
      localStorage.age !== "undefined" &&
      localStorage.gender !== "undefined" &&
      localStorage.education !== "undefined" &&
      localStorage.occupation !== "undefined" &&
      localStorage.family_size !== "undefined" &&
      // family occupation is optional
      localStorage.family_income !== "undefined" &&
      localStorage.has_mobile !== "undefined" &&
      localStorage.watch_video !== "undefined" &&
      localStorage.internet_phone !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
    }

    if (step === 8) { // final code
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
    var raw_html = '<strong>Watch in fullscreen mode and use headphones.</strong>' +
      '<video width="320" height="240" id="{0}" onplay="naf.play_started()" controls>' +
      '<source src="/static/videos/{0}" type="video/mp4">' +
      'Your browser does not support the video.' +
      '</video>';
    raw_html = raw_html.format(mp4);
    return raw_html;
  }

  function get_survey(step, worker_group) {
    var order = get_content_order(step, worker_group);
    var vid;
    if (step === 1) {
      vid = 'v1';
    } else if (step === 3) {
      vid = 'v2';
    } else if (step === 5) {
      vid = 'v3';
    }

    var form = '<form onclick="check_video_survey()">' +
      '<div class="form-group">' +
      '<label for="">Using the image below, indicate how happy or sad you feel after watching the video. Please tick the figure that best represents your feelings. </label>' +
      '<img src="/static/images/naf/valence.png" width="550px" height="150px" alt="valence image" />' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q1" value="1"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q1" value="2"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q1" value="3"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q1" value="4"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q1" value="5"/>' +
      '</label>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      '<label for="">Using the image below, please indicate how the video affects you. Select the figure that best represents your feelings.</label>' +
      '<img src="/static/images/naf/arousal.png" width="550px" height="150px" alt="arousal image" />' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q2" value="1"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q2" value="2"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q2" value="3"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q2" value="4"/>' +
      '</label>' +
      '<label class="naf-radio">' +
      '<input type="radio" name="{0}q2" value="5"/>' +
      '</label>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      '<label for="">What was the topic of the video?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="1"/> Nutrition of newborn' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="2"/> Dangerous effects of smoking and tobacco' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="3"/> Importance of washing hands' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="4"/> Safe drinking water' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="5"/> Treatment of Diarrhea' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="5"/> None of these' +
      '</span>' +
      '</div>' +
      '</form>';

    form = form.format(vid);
    return form;
  }

  function get_demography_survey() {
    var form = '<form class="demography" onclick="check_demogr()">' +
      '<div class="form-group">' +
      '<label>What is your age?</label>' +
      '<input type="number" class="form-control" id="demogr-age" placeholder="enter number">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="">What is your gender</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-gender" value="male"/> Male' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-gender" value="female"/> Female' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-gender" value="other"/> Other' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="">What is the your highest level of education?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-education" value="primary"/> Primary School' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-education" value="secondary"/> Secondary School (10th)' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-education" value="higher_secondary"/> Higher Secondary School (12th)' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-education" value="bachelors"/> Bachelors' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-education" value="masters"/> Masters' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      '<label>What is your occupation?</label>' +
      '<input type="text" class="form-control" id="demogr-occupation" placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What is your family size?</label>' +
      '<input type="number" class="form-control" id="demogr-family-size" placeholder="enter number">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What is the occupation of your family members?</label>' +
      '<input type="text" class="form-control" id="demogr-family-occupation" placeholder="optional response here">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="formGroupExampleInput">What is your monthly family income?</label>' +
      '<input type="number" class="form-control" id="demogr-family-income" placeholder="number in rupees">' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="">Do you have a mobile phone?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-has-mobile" value="no_share"/> Yes, I own one but do NOT share it.' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-has-mobile" value="yes_share"/> Yes, I own one and I share it.' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-has-mobile" value="no_phone"/> I do not have a mobile phone.' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="">Do you watch videos on your mobile phone</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-watch-video" value="yes"/> Yes' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-watch-video" value="no"/> No' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="">Do you use Internet on phone?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-internet-phone" value="yes"/> Yes' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="demogr-internet-phone" value="no"/> No' +
      '</span>' +
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

// survey1
localStorage.v1q1 = "undefined";
localStorage.v1q2 = "undefined";
localStorage.v1q3 = "undefined";

// survey2
localStorage.v2q1 = "undefined";
localStorage.v2q2 = "undefined";
localStorage.v2q3 = "undefined";

// survey3
localStorage.v3q1 = "undefined";
localStorage.v3q2 = "undefined";
localStorage.v3q3 = "undefined";

// demography survey
localStorage.age = "undefined";
localStorage.gender = "undefined";
localStorage.education = "undefined";
localStorage.occupation = "undefined";
localStorage.family_size = "undefined";
localStorage.family_occupation = "undefined";
localStorage.family_income = "undefined";
localStorage.has_mobile = "undefined";
localStorage.watch_video = "undefined";
localStorage.internet_phone = "undefined";


function check_demogr() {
  console.log('oncick demogr called');
  checkSurvey('demography');
}

function check_video_survey() {
  var current_step = parseInt($('#step-value').text());
  if (current_step === 2) {
    checkSurvey('v1');
  } else if (current_step === 4) {
    checkSurvey('v2');
  } else if (current_step === 6) {
    checkSurvey('v3');
  }
}

function checkSurvey(name) {
  // survey1
  if (name === 'v1') {
    console.log('completing v1 survey');
    localStorage.v1q1 = $('input[name=v1q1]:checked').val();
    localStorage.v1q2 = $('input[name=v1q2]:checked').val();
    localStorage.v1q3 = $('input[name=v1q3]:checked').val();
    console.log(localStorage.v1q1, localStorage.v1q2, localStorage.v1q3);

    if (localStorage.v1q1 !== "undefined" && localStorage.v1q2 !== "undefined" && localStorage.v1q3 !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
      console.log('Will enable next button for step 3.');
    }
  }

  // survey2
  else if (name === 'v2') {
    console.log('completing v2 survey');
    localStorage.v2q1 = $('input[name=v2q1]:checked').val();
    localStorage.v2q2 = $('input[name=v2q2]:checked').val();
    localStorage.v2q3 = $('input[name=v2q3]:checked').val();
    console.log(localStorage.v2q1, localStorage.v2q2, localStorage.v2q3);

    if (localStorage.v2q1 !== "undefined" && localStorage.v2q2 !== "undefined" && localStorage.v2q3 !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
      console.log('Will enable next button for step 5.');
    }
  }

  // survey3
  else if (name === 'v3') {
    console.log('completing v3 survey');
    localStorage.v3q1 = $('input[name=v3q1]:checked').val();
    localStorage.v3q2 = $('input[name=v3q2]:checked').val();
    localStorage.v3q3 = $('input[name=v3q3]:checked').val();
    console.log(localStorage.v3q1, localStorage.v3q2, localStorage.v3q3);

    if (localStorage.v3q1 !== "undefined" && localStorage.v3q2 !== "undefined" && localStorage.v3q3 !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
      console.log('Will enable next button for step 7.');
    }
  }

  // demography
  else if (name === 'demography') {
    localStorage.age = $('#demogr-age').val();
    localStorage.gender = $('input[name=demogr-gender]:checked').val();
    localStorage.education = $('input[name=demogr-education]:checked').val();
    localStorage.occupation = $('#demogr-occupation').val();
    localStorage.family_size = $('#demogr-family-size').val();
    localStorage.family_occupation = $('#demogr-family-occupation').val();
    localStorage.family_income = $('#demogr-family-income').val();
    localStorage.has_mobile = $('input[name=demogr-has-mobile]:checked').val();
    localStorage.watch_video = $('input[name=demogr-watch-video]:checked').val();
    localStorage.internet_phone = $('input[name=demogr-internet-phone]:checked').val();

    if (localStorage.age !== "undefined" &&
      localStorage.gender !== "undefined" &&
      localStorage.education !== "undefined" &&
      localStorage.occupation !== "undefined" &&
      localStorage.family_size !== "undefined" &&
      // family occupation is optional
      localStorage.family_income !== "undefined" &&
      localStorage.has_mobile !== "undefined" &&
      localStorage.watch_video !== "undefined" &&
      localStorage.internet_phone !== "undefined") {
      $('#next-step-btn').prop('disabled', false);
    }

  }
}
