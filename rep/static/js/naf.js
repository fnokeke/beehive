/*jshint multistr: true */
var naf = (function() {
  var g_video_played = false;
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

  $('#btn-begin-step').click(function() {
    $('#steps-modal').modal('show');
    $('#next-step-btn').hide();

    var worker_group = parseInt($('#worker-group').text());
    var current_step = parseInt($('#step-value').text());
    countdown_next_step_btn(current_step, worker_group);
    show_workers_quotes();
  });

  $('#hindi-test-response-btn').click(function() {
    var response = parseInt($('#hindi-test-response').val());
    console.log('response: ', response);
    if (response === 17) {
      $('#begin-div').hide();
      $('#submit-div').show();
    } else {
      alert('No need to continue with study.');
      location.reload();
    }
  });

  // #############################################
  // ############ HINDI GOOGLE FORMS ################
  // #############################################
  $('#hindi-test-response-btn-nafa').click(function() {
    var response = parseInt($('#hindi-test-response-nafa').val());
    console.log('response: ', response);
    if (response === 17) {
      $('#begin-div-nafa').hide();
      $('#survey-div-nafa').show();
    } else {
      alert('You cannot continue with Study. Please close this page.');
      location.reload();
    }
  });

  $('#hindi-test-response-btn-nafb').click(function() {
    var response = parseInt($('#hindi-test-response-nafb').val());
    console.log('response: ', response);
    if (response === 17) {
      $('#begin-div-nafb').hide();
      $('#survey-div-nafb').show();
    } else {
      alert('You cannot continue with Study. Please close this page.');
      location.reload();
    }
  });


  $('#hindi-test-response-btn-nafc').click(function() {
    var response = parseInt($('#hindi-test-response-nafc').val());
    console.log('response: ', response);
    if (response === 17) {
      $('#begin-div-nafc').hide();
      $('#survey-div-nafc').show();
    } else {
      alert('You cannot continue with Study. Please close this page.');
      location.reload();
    }
  });


  $('#hindi-test-response-btn-nafd').click(function() {
    var response = parseInt($('#hindi-test-response-nafd').val());
    console.log('response: ', response);
    if (response === 17) {
      $('#begin-div-nafd').hide();
      $('#survey-div-nafd').show();
    } else {
      alert('You cannot continue with Study. Please close this page.');
      location.reload();
    }
  });


  $('#hindi-test-response-btn-nafe').click(function() {
    var response = parseInt($('#hindi-test-response-nafe').val());
    console.log('response: ', response);
    if (response === 17) {
      $('#begin-div-nafe').hide();
      $('#survey-div-nafe').show();
    } else {
      alert('You cannot continue with Study. Please close this page.');
      location.reload();
    }
  });

  $('#hindi-test-response-btn-naff').click(function() {
    var response = parseInt($('#hindi-test-response-naff').val());
    console.log('response: ', response);
    if (response === 17) {
      $('#begin-div-naff').hide();
      $('#survey-div-naff').show();
    } else {
      alert('You cannot continue with Study. Please close this page.');
      location.reload();
    }
  });
  // #############################################
  // #############################################

  $("#steps-modal").on("hidden.bs.modal", function() {
    clear_all_timers();

    g_video_played = false;
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    var return_to_step = is_reveal_code_step(current_step, worker_group) ? current_step : 1;
    $('#step-value').text(return_to_step);


    if (return_to_step === 1) {
      wipe_then_init_values();
      console.log('Reset back to beginning.');
    } else {
      $('#next-step-btn').show();
    }

    var vid = $('video').get(0);
    if (vid) {
      vid.pause();
    }

  });

  function clear_all_timers() {
    clearTimeout(parseInt(localStorage.do_countdown_id));
    clearInterval(parseInt(localStorage.spinner_intv_id));
    clearTimeout(parseInt(localStorage.display_video_ready_id));
    clearTimeout(parseInt(localStorage.qid1));
    clearTimeout(parseInt(localStorage.qid2));
    clearTimeout(parseInt(localStorage.qid3));

  // console.log('localStorage.do_countdown_id: ', localStorage.do_countdown_id);
  // console.log('localStorage.spinner_intv_id: ', localStorage.spinner_intv_id);
  // console.log('localStorage.display_video_ready_id: ', localStorage.display_video_ready_id);
  // console.log('localStorage.qid1: ', localStorage.qid1);
  // console.log('localStorage.qid2: ', localStorage.qid2);
  // console.log('localStorage.qid3: ', localStorage.qid3);
  }

  $('#naf-read-consent-btn').click(function() {
    $('#naf-consent-agree-modal').modal('show');
  });

  $('#naf-consent-agreed-btn').click(function() {
    $('#naf-consent-agree-modal').modal('hide');
    $('#naf-hindi-test-div').show();
    localStorage.agreed_to_consent = "true";
  });

  (function agreed_to_consent() {
    if (localStorage.agreed_to_consent === "true") {
      $('#naf-hindi-test-div').show();
    }
  })();

  $('#next-step-btn').click(function() {
    update_steps();
  });

  function update_steps() {
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    var worker_code = $('#worker-code').text();

    var url = '/naf/update/step';
    var data = {
      'current_step': current_step
    };

    $.post(url, data).done(function(resp) {
      var json_resp = JSON.parse(resp);
      $('#step-value').text(json_resp.next_step);
      $('#span-begin-label').text(get_btn_step_content(json_resp.next_step, worker_group));
      $('#modal-title-value').html(get_modal_title(json_resp.next_step, worker_group));
      $('#modal-body-content').html(get_modal_body(json_resp.next_step, worker_group, worker_code));

      $('#next-step-btn').prop('disabled', true);
      g_video_played = false;

      if (is_demography_step(current_step, worker_group)) {
        $('#next-step-btn').hide();
      }

      countdown_next_step_btn(json_resp.next_step, worker_group);
    }).fail(function(error) {
      $('#next-step-btn').prop('disabled', true);
      console.log('step error: ', error);
    });

    $('#next-step-btn').prop('disabled', true);
  }


  function play_started() {
    g_video_played = true;
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    countdown_next_step_btn(current_step, worker_group);
  }

  // for group 3 worker, only step 1 has video (main video)
  // for other groups, steps 1 and 2 have priming and then main video respectively
  function step_has_video(step, worker_group) {
    if (worker_in_group3(worker_group)) {
      return step === 1;
    }
    return step < 3;
  }

  function is_valid(entry) {
    return entry !== "" && entry !== "undefined";
  }

  function is_valid_stored_demogr_survey() {
    return is_valid(localStorage.city) &&
      is_valid(localStorage.age) &&
      is_valid(localStorage.gender) &&
      is_valid(localStorage.education) &&
      is_valid(localStorage.occupation) &&
      is_valid(localStorage.family_size) &&
      // family occupation is optional
      is_valid(localStorage.family_income) &&
      is_valid(localStorage.has_mobile) &&
      is_valid(localStorage.watch_video) &&
      is_valid(localStorage.internet_phone);
  }

  function is_main_survey_step(step, worker_group) {
    if (worker_in_group3(worker_group)) {
      return step === 2;
    }
    return step === 3;
  }

  function is_demography_step(step, worker_group) {
    if (worker_in_group3(worker_group)) {
      return step === 3;
    }
    return step === 4;
  }

  function is_reveal_code_step(step, worker_group) {
    step = parseInt(step);
    worker_group = parseInt(worker_group);
    if (worker_in_group3(worker_group)) {
      return step === 4;
    }
    return step === 5;
  }

  function countdown_next_step_btn(step, worker_group) {
    $('#next-step-btn').prop('disabled', true);

    if (step_has_video(step, worker_group) && g_video_played) {
      console.log('countdown step has video');
      do_video_countdown(step, worker_group);
    }

    // main survey completed
    if (is_main_survey_step(step, worker_group) &&
      is_valid(localStorage.mainq1) &&
      is_valid(localStorage.mainq2) &&
      is_valid(localStorage.mainq3) &&
      is_valid(localStorage.mainq4) &&
      is_valid(localStorage.mainq5)) {
      $('#next-step-btn').prop('disabled', false);
    }

    // demography survey completed
    if (is_demography_step(step, worker_group) &&
      is_valid(localStorage.city) &&
      is_valid(localStorage.age) &&
      is_valid(localStorage.gender) &&
      is_valid(localStorage.education) &&
      is_valid(localStorage.occupation) &&
      is_valid(localStorage.family_size) &&
      // family occupation is optional
      is_valid(localStorage.family_income) &&
      is_valid(localStorage.has_mobile) &&
      is_valid(localStorage.watch_video) &&
      is_valid(localStorage.internet_phone)) {
      $('#next-step-btn').prop('disabled', false);
    }

    if (is_reveal_code_step(step, worker_group)) { // final code
      $('#next-step-btn').hide();
      if (localStorage.submitted !== "true") {
        submit_data();
        console.log('Making first submission.');
      } else {
        console.log('Already submitted before.');
      }
    }
  }

  function submit_data() {
    var worker_id = window.location.href.split("/")[4];
    if (localStorage.age === "") {
      localStorage.age = 0;
    }

    var data = {
      'worker_id': worker_id,
      //  main / artifact video
      'mainq1': parseInt(localStorage.mainq1),
      'mainq2': parseInt(localStorage.mainq2),
      'mainq3': parseInt(localStorage.mainq3),
      'mainq4': parseInt(localStorage.mainq4),
      'mainq5': parseInt(localStorage.mainq5),
      'mainq6': localStorage.mainq6,
      'mainq7': localStorage.mainq7,
      // demography
      'city': localStorage.city,
      'age': parseInt(localStorage.age),
      'gender': localStorage.gender,
      'education': localStorage.education,
      'occupation': localStorage.occupation,
      'family_size': parseInt(localStorage.family_size),
      'family_occupation': localStorage.family_occupation,
      'family_income': parseInt(localStorage.family_income),
      'has_mobile': localStorage.has_mobile,
      'watch_video': localStorage.watch_video,
      'internet_phone': localStorage.internet_phone
    };
    console.log('data to submit: ', data);

    var url = '/naf/submit';

    $.post(url, data).done(function(resp) {
      var json_resp = JSON.parse(resp);
      if (json_resp.status === 200) {
        $('#next-step-btn').prop('disabled', false);
        localStorage.submitted = "true";
        console.log('Successfully submitted data.');
      } else {
        alert('Error, contact requester.\nError: ' + resp.statusText);
      }
    }).fail(function(error) {
      console.log('error: ', error);
      $('#next-step-btn').prop('disabled', true);
      alert('Error. Please notify Mturk requester.\nError: ' + error.statusText);
    });

  }

  function do_countdown(seconds) {
    localStorage.do_countdown_id = setTimeout(function() {
      $('#next-step-btn').prop('disabled', false);
    }, seconds * 1000);
  }

  function do_video_countdown(step, worker_group) {
    // do_countdown(167);
    do_countdown(1);
  // if (worker_in_group3(worker_group) && step === 1) {
  //   // do_countdown(1);
  //   do_countdown(167);
  // } else if (!worker_in_group3(worker_group) && step === 1) {
  //   // do_countdown(65);
  //   do_countdown(167);
  // } else if (!worker_in_group3(worker_group) && step === 2) {
  //   // do_countdown(1);
  //   do_countdown(167);
  // }
  }

  function get_btn_step_content(step, worker_group) {
    // var contents = "Begin Step " + step;
    var contents = "स्टेप " + step + " को शुरू करें";

    if (is_reveal_code_step(step, worker_group)) {
      contents = "Show mturk code";
    }
    return contents;
  }

  function worker_in_group3(worker_group) {
    return worker_group % 3 === 0;
  }

  function get_modal_body(step, worker_group, worker_code) {
    return get_contents_group3(step, worker_group);
  // var contents = '';
  // if (worker_in_group3(worker_group)) {
  //   return get_contents_group3(step, worker_group);
  // } else {
  //   return get_contents_group1_group2(step, worker_group);
  // }
  }

  function get_contents_group3(step, worker_group) {
    var msg;
    var video_name;
    var worker_code;
    var contents;

    if (step === 1) {
      msg = 'नीचे दिए हुए वीडियो को बहुत ध्यान से देखें। यह वीडियो लगभग 3 मिनट का है। इस वीडियो को देखने के बाद आपको हमें बताना होगा की यह वीडियो आपको कैसा लगा?';
      contents = get_video(msg, 'main.mp4');
    } else if (step === 2) {
      msg = 'जो वीडियो आपने अभी अभी देखा, सिर्फ उसके आधार पर कृपया इन 5 सवालों के जवाब दे। हम चाहेंगे कि आप इन सवालों का जवाब ईमानदारी से दें।';
      contents = get_main_survey(msg);
    } else if (step === 3) {
      contents = get_demography_survey();
    } else if (step === 4) {
      worker_code = $('#worker-code').text();
      contents = 'आपका MTurk Code  है: ' + worker_code;
    // contents = 'Your mturk code: ' + worker_code;
    }
    return contents;
  }

  function get_contents_group1_group2(step, worker_group) {
    var msg;
    var video_name;
    var worker_code;
    var contents;

    if (step === 1) {
      msg = "नीचे दिए हुए वीडियो को ध्यान से fullscreen mode पर देखें।  अपने headphones का इस्तेमाल करें।  यह वीडियो सिर्फ 1 मिनट का है।";
      video_name = worker_group % 2 === 0 ? "neg.mp4" : "pos.mp4";
      contents = get_video(msg, video_name);
    } else if (step === 2) {
      msg = 'नीचे दिए हुए वीडियो को बहुत ध्यान से देखें। यह वीडियो लगभग 3 मिनट का है। इस वीडियो को देखने के बाद आपको हमें बताना होगा की यह वीडियो आपको कैसा लगा? ध्यान दें की इस वीडियो को पहले देखे हुए वीडियो (स्टेप 1 ) से compare नहीं करें।';
      contents = get_video(msg, 'main.mp4');
    } else if (step === 3) {
      msg = 'जो वीडियो आपने अभी अभी देखा (स्टेप 2 में ), सिर्फ उसके आधार पर कृपया इन 5 सवालों के जवाब दे।  हम चाहेंगे कि आप इन सवालों का जवाब ईमानदारी से दें।';
      contents = get_main_survey(msg);
    } else if (step === 4) {
      contents = get_demography_survey();
    } else if (step === 5) {
      worker_code = $('#worker-code').text();
      contents = 'आपका MTurk Code  है: ' + worker_code;
    // contents = 'Your mturk code: ' + worker_code;
    }

    return contents;
  }


  function get_modal_title(step, worker_group) {
    // var total_steps = worker_in_group3(worker_group) ? 3 : 4;
    var total_steps = 3;

    // var contents = "Step " + step + " of 5";
    var contents = "स्टेप " + step + " / " + total_steps;
    if (step > total_steps) {
      // contents = "Submit mturk code";
      contents = "अपने MTurk Code को सबमिट करें।";
    }
    return contents;
  }

  function get_video(msg, video_name) {
    var raw_html = '<div id="mainVideoDiv" class="noshow"><strong>{0}</strong><br><br>' +
      '<video width="550" height="300" id="{0}" onplay="naf.play_started()" controls>' +
      '<source src="/static/videos/compressed/{1}" type="video/mp4">' +
      'Your browser does not support the video.' +
      '</video></div>';

    raw_html = raw_html.format(msg, video_name);
    return get_slide_html() + raw_html;
  }

  function get_main_survey(msg) {
    var vid = "main";
    var form = '<form onchange="naf.check_main_survey()">' +
      '<strong>' + msg + '</strong>' +
      '<br>' +
      '<br>' +
      '<div class="form-group">' +
      // '<label for="">How much did you like the last video?</label>' +
      '<label for="">आपको यह विडियो कैसा लगा?</label>' +
      '<img src="/static/images/naf/valence2.png" width="550px" height="150px" alt="valence image" />' +
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
      // '<label for="">How useful was the last video to you?</label>' +
      '<label for="">आपको यह विडियो देख कर कुछ फायदा हुआ?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="1"/> कोई फायदा नहीं हुआ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="2"/> थोड़ा फायदा हुआ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="3"/> ठीक-ठाक फायदा हुआ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="4"/> ज्यादा फायदा हुआ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="5"/> बहुत ज्यादा फायदा हुआ' +
      '</span>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      // '<label for="">How entertaining was the last video to you?</label>' +
      '<label for="">आपको यह विडियो कितना मनोरंजक लगा?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="1"/> बहुत उबाऊ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="2"/> थोड़ा उबाऊ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="3"/> ना उबाऊ ना मनोरंजक' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="4"/> थोड़ा मनोरंजक' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="5"/> बहुत मनोरंजक' +
      '</span>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      // '<label for="">How can the last video be improved?</label>' +
      '<label for="">क्या इस विडियो को और सुधारा जा सकता है</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q4" value="1"/> कोई सुधार की जरूरत नहीं है' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q4" value="2"/> बहुत कम सुधार की जरूरत है' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q4" value="3"/> कम सुधार की जरूरत है' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q4" value="4"/> ज्यादा सुधार की जरूरत है' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q4" value="5"/> बहुत ज्यादा सुधार की जरूरत है' +
      '</span>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      // '<label for="">What was the video about?</label>' +
      '<label for="">यह वीडियो किस विषय पर था ?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q5" value="1"/> नवजात बच्चे के पोषण के बारे में' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q5" value="2"/> धूम्रपान करने के और तम्बाकू खाने के नुकसान' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q5" value="3"/> साफ़ पानी पीने के बारे में' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q5" value="4"/> दस्त के इलाज के बारे में' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q5" value="5"/> इनमे से कोई नहीं' +
      '</span>' +
      '</div>' +
      '<br>' +
      '<br>' +
      '<div class="form-group">' +
      // '<label for="">Please leave a review for the video you watched. Tell us what you liked or did not like about the video.</label>' +
      '<label for="">अभी जो आपने वीडियो देखा, आप उस वीडियो पर अपना review लिख सकते हैं।  कृपया हमें बताएं कि आपको क्या अच्छा लगा और क्या अच्छा नहीं लगा।</label>' +
      '<br/>' +
      '<span>' +
      '<textarea id="{0}q6" rows="8" cols="60" placeholder="Optional. Response can be in English or Hindi."></textarea>' +
      '</span>' +
      '</div>' +
      '<br>' +
      '<br>' +
      '<div class="form-group">' +
      // '<label for="">Any other comments or thoughts?</label>' +
      '<label for="">और कोई प्रतिक्रिया या सुझाव ?</label>' +
      '<br/>' +
      '<span>' +
      '<textarea id="{0}q7" rows="8" cols="60" placeholder="Optional. Response can be in English or Hindi."></textarea>' +
      '</span>' +
      '</div>' +
      '</form>';

    form = form.format(vid);
    return form;
  }

  function get_demography_survey() {
    var form = '<form class="demography" onclick="naf.check_demogr_survey()">' +
      '<div class="form-group">' +
      // '<label>In what city you live</label>' +
      '<label>आप किस शहर में रहते हैं?</label>' +
      '<input type="text" class="form-control" id="demogr-city">' +
      '</div>' +
      '<div class="form-group">' +
      // '<label>What is your age?</label>' +
      '<label>आपकी उम्र क्या है ?</label>' +
      '<input type="number" class="form-control" id="demogr-age" placeholder="enter number">' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="">What is your gender</label>' +
      '<label for="">आपका gender  क्या है?</label>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-gender" value="male"/> Male' +
      '<input type="radio" name="demogr-gender" value="male"/> मेल' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-gender" value="female"/> Female' +
      '<input type="radio" name="demogr-gender" value="female"/> फीमेल' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-gender" value="other"/> Other' +
      '<input type="radio" name="demogr-gender" value="other"/> Other' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="">What is the your highest level of education?</label>' +
      '<label for="">आपने कहाँ तक पढ़ाई की है?</label>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-education" value="primary"/> Primary School' +
      '<input type="radio" name="demogr-education" value="primary"/> प्राइमरी स्कूल (पांचवी तक)' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-education" value="secondary"/> Secondary School (10th)' +
      '<input type="radio" name="demogr-education" value="secondary"/> सेकेंडरी स्कूल (दसवीं तक)' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-education" value="higher_secondary"/> Higher Secondary School (12th)' +
      '<input type="radio" name="demogr-education" value="higher_secondary"/> हायर सेकेंडरी स्कूल (बारवीं तक)' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-education" value="bachelors"/> Bachelors' +
      '<input type="radio" name="demogr-education" value="bachelors"/> ग्रेजुएशन' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-education" value="masters"/> Masters' +
      '<input type="radio" name="demogr-education" value="masters"/> पोस्ट ग्रेजुएशन' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-education" value="none"/> Masters' +
      '<input type="radio" name="demogr-education" value="none"/> इनमें से कोई नहीं' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      // '<label>What is your occupation?</label>' +
      '<label>आप क्या काम करते है?</label>' +
      '<input type="text" class="form-control" id="demogr-occupation" max=50 placeholder="type response here">' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="formGroupExampleInput">What is your family size?</label>' +
      '<label for="formGroupExampleInput">आपके परिवार में कितने लोग है ?</label>' +
      '<input type="number" class="form-control" id="demogr-family-size" max=50 placeholder="enter number">' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="formGroupExampleInput">What is the occupation of your family members?</label>' +
      '<label for="formGroupExampleInput">आपके परिवार के सदस्य क्या काम करते है ?</label>' +
      '<input type="text" class="form-control" id="demogr-family-occupation" placeholder="optional response here">' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="formGroupExampleInput">What is your monthly family income?</label>' +
      '<label for="formGroupExampleInput">आपके परिवार की महीने की आमदनी क्या है ?</label>' +
      '<input type="number" class="form-control" id="demogr-family-income" placeholder="number in rupees">' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="">Do you have a mobile phone?</label>' +
      '<label for="">क्या आपके पास मोबाइल फ़ोन है?</label>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-has-mobile" value="no_share"/> Yes, I own one but do NOT share it.' +
      '<input type="radio" name="demogr-has-mobile" value="no_share"/> हाँ, मेरा खुद का है लेकिन और कोई भी इस मोबाइल का इस्तेमाल करता है ' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-has-mobile" value="yes_share"/> Yes, I own one and I share it.' +
      '<input type="radio" name="demogr-has-mobile" value="yes_share"/> हाँ, मेरा खुद का है लेकिन और कोई इस मोबाइल का इस्तेमाल नहीं करता है' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-has-mobile" value="no_phone"/> I do not have a mobile phone.' +
      '<input type="radio" name="demogr-has-mobile" value="no_phone_but_share"/> नहीं, मेरे पास मोबाइल नहीं है लेकिन मैं किसी और का मोबाइल इस्तेमाल करता हूँ ' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-has-mobile" value="no_phone"/> I do not have a mobile phone.' +
      '<input type="radio" name="demogr-has-mobile" value="no_phone_at_all"/> नहीं, मेरे पास मोबाइल नहीं हैूँ ' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="">Do you watch videos on your mobile phone</label>' +
      '<label for="">क्या आप अपने फ़ोन पर वीडियो  देखते  है?</label>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-watch-video" value="yes"/> Yes' +
      '<input type="radio" name="demogr-watch-video" value="yes"/> हाँ' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-watch-video" value="no"/> No' +
      '<input type="radio" name="demogr-watch-video" value="no"/> नहीं' +
      '</span>' +
      '</div>' +
      '<div class="form-group">' +
      // '<label for="">Do you use Internet on phone?</label>' +
      '<label for="">क्या आप अपने फ़ोन पर इंटरनेट का इस्तेमाल करते है?</label>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-internet-phone" value="yes"/> Yes' +
      '<input type="radio" name="demogr-internet-phone" value="yes"/> हाँ' +
      '</span>' +
      '<br>' +
      '<span>' +
      // '<input type="radio" name="demogr-internet-phone" value="no"/> No' +
      '<input type="radio" name="demogr-internet-phone" value="no"/> नहीं' +
      '</span>' +
      '</div>' +
      '</form>';
    return form;
  }

  $('#mainq4').on('change', function() {
    check_main_survey();
  });

  function check_main_survey() {
    localStorage.mainq1 = $('input[name=mainq1]:checked').val();
    localStorage.mainq2 = $('input[name=mainq2]:checked').val();
    localStorage.mainq3 = $('input[name=mainq3]:checked').val();
    localStorage.mainq4 = $('input[name=mainq4]:checked').val();
    localStorage.mainq5 = $('input[name=mainq5]:checked').val();
    localStorage.mainq6 = $('#mainq6').val();
    localStorage.mainq7 = $('#mainq7').val();

    if (is_valid(localStorage.mainq1) &&
      is_valid(localStorage.mainq2) &&
      is_valid(localStorage.mainq3) &&
      is_valid(localStorage.mainq4) &&
      is_valid(localStorage.mainq5)) {
      console.log('Next step enabled for main survey.');
      $('#next-step-btn').prop('disabled', false);
    } else {
      console.log('Waiting to enable next btn');
    }
  }

  function check_demogr_survey() {
    localStorage.city = $('#demogr-city').val();
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

    if (is_valid_stored_demogr_survey()) {
      $('#next-step-btn').prop('disabled', false);
    }
  }


  function wipe_then_init_values() {
    localStorage.clear();
    // localStorage.agreed_to_consent = "true";
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    var worker_code = $('#worker-code').text();
    $('#span-begin-label').text(get_btn_step_content(current_step, worker_group));
    $('#modal-title-value').html(get_modal_title(current_step, worker_group));
    $('#modal-body-content').html(get_modal_body(current_step, worker_group, worker_code));
    countdown_next_step_btn(current_step, worker_group);
  }
  wipe_then_init_values();

  function current_worker_in_group3() {
    var worker_group = parseInt($('#worker-group').text());
    return worker_in_group3(worker_group);
  }

  function get_slide_html() {
    return '<div id="mturkSlideShow">' +
      '<div id="quoteDiv">' +
      '<h4>' +
      // ' Please wait. Your video is loading...' +
      'कृपया थोड़ा इंतज़ार करें। वीडियो लोड हो रहा है' +
      '</h4>' +
      '<br>' +

      '<div id="readReviewDiv">' +
      '<h4>' +
      // ' While you wait, you can read reviews of the video submitted by mTurk workers like you.' +
      'जब तक आप इंतज़ार कर रहे हैं, आपके जैसे  MTurk workers ने इस वीडियो पर जो reviews दिए हैं उनको आप पढ़ सकते हैं।.' +
      '</h4>' +
      ' <br>' +

      '</div>' +
      ' <div id="quote1" class="noshow text-center"></div>' +
      ' <div id="quote2" class="noshow text-center"></div>' +
      ' <div id="quote3" class="noshow text-center"></div>' +
      '</div>' +

      '<div class="sk-circle" id="videoLoadingDiv">' +
      ' <div class="sk-child" id="percentDiv"></div>' +
      ' <div class="sk-circle1 sk-child"></div> ' +
      ' <div class="sk-circle2 sk-child"></div> ' +
      ' <div class="sk-circle3 sk-child"></div> ' +
      ' <div class="sk-circle4 sk-child"></div> ' +
      ' <div class="sk-circle5 sk-child"></div> ' +
      ' <div class="sk-circle5 sk-child"></div> ' +
      ' <div class="sk-circle6 sk-child"></div> ' +
      ' <div class="sk-circle7 sk-child"></div> ' +
      ' <div class="sk-circle8 sk-child"></div> ' +
      ' <div class="sk-circle9 sk-child"></div> ' +
      ' <div class="sk-circle10 sk-child"></div> ' +
      ' <div class="sk-circle11 sk-child"></div> ' +
      ' <div class="sk-circle12 sk-child"></div> ' +
      '</div> ' +

      '<div id="videoReadyDiv" class="noshow text-center">' +
      // 'Video is ready.' +
      'आपका वीडियो लोड हो गया है.' +
      '<br>' +
      '<button' +
      '  type="button"' +
      '  name="button"' +
      '  class="btn btn-primary"' +
      '  id="continueToVideo"' +
      // '  onclick="show_main_video()">Click to Continue ' +
      '  onclick="show_main_video()">Continue करने के लिए क्लिक करें' +
      '</button>' +
      ' </div>' +
      '</div>';

  }


  var exposed_functions = {
    'current_worker_in_group3': current_worker_in_group3,
    'check_main_survey': check_main_survey,
    'check_demogr_survey': check_demogr_survey,
    'play_started': play_started,
  };

  return exposed_functions;

})();


// main/artifact survey
localStorage.mainq1 = "undefined";
localStorage.mainq2 = "undefined";
localStorage.mainq3 = "undefined";
localStorage.mainq4 = "undefined";
localStorage.mainq5 = "undefined";

// demography survey
localStorage.city = "undefined";
localStorage.age = "undefined";
localStorage.gender = "undefined";
localStorage.education = "undefined";
localStorage.occupation = "undefined";
localStorage.family_size = "undefined";
localStorage.family_occupation = "skip"; // optional for participant
localStorage.family_income = "undefined";
localStorage.has_mobile = "undefined";
localStorage.watch_video = "undefined";
localStorage.internet_phone = "undefined";


function show_workers_quotes() {
  var worker_group = parseInt($('#qt-wk-group').val());
  var default_wait = 5; // seconds
  var quote_wait = 7; // seconds

  if (worker_group === 3) {
    removeReviewGuide();
  } else {
    countdown_then_display_quote(1, default_wait); // 5
    countdown_then_display_quote(2, default_wait + quote_wait); // 15
    countdown_then_display_quote(3, default_wait + 2 * quote_wait); // 25
  }
  display_video_ready(default_wait + 3 * quote_wait); // 35
  show_spinner_percent(default_wait + 3 * quote_wait); // 35
}

function removeReviewGuide() {
  $('#readReviewDiv').hide();
}

function show_spinner_percent(total_seconds) {
  var percent = 1;
  var interval = 1000 * total_seconds / 99;
  var percentDiv = '#percentDiv';
  $(percentDiv).show();

  localStorage.spinner_intv_id = setInterval(update_percent, 1000 * total_seconds / 99);
  function update_percent() {
    percent++;
    $(percentDiv).text(percent + "%");
    if (percent >= 100) {
      $(percentDiv).hide();
      clearInterval(parseInt(localStorage.spinner_intv_id));
    }
  }
}

function countdown_then_display_quote(num, seconds) {
  localStorage['qid' + num] = setTimeout(function() {
    show_quote(num);
  }, seconds * 1000);
}

function show_quote(num) {
  var qid,
    qidValue,
    percent;
  $('#btnViewQuotes').prop('disabled', true);
  $('#quote1').hide();
  $('#quote2').hide();
  $('#quote3').hide();

  qid = '#quote' + num;
  qidValue = $('#qt' + num).val();
  qidValue = '<h3><em>"' + qidValue + '"</em></h3>';
  $(qid).html(qidValue);
  $(qid).show();

}

function display_video_ready(seconds) {
  localStorage.display_video_ready_id = setTimeout(function() {
    $('#videoLoadingDiv').hide();
    $('#videoReadyDiv').show();
  }, seconds * 1000);
}


function show_main_video() {
  console.log('Now showing main video');
  $('#videoReadyDiv').hide();
  $('#quoteDiv').hide();
  $('#next-step-btn').show();
  $('#mainVideoDiv').show();
}
