/*jshint multistr: true */
var naf = (function() {
  var g_video_played = false;
  // var g_worker_group = parseInt($('#worker-group').text());

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
    $('#next-step-btn').show();

    var worker_group = parseInt($('#worker-group').text());
    var current_step = parseInt($('#step-value').text());
    countdown_next_step_btn(current_step, worker_group);
  });

  $('#begin-response-btn').click(function() {
    var response = $('#begin-response-text').val();
    console.log('response: ', response);
    if (response === '20') {
      $('#begin-div').hide();
      $('#submit-div').show();
    } else {
      alert('No need to continue with study.');
      location.reload();
    }
  });

  $("#steps-modal").on("hidden.bs.modal", function() {
    var current_step = $('#step-value').text();
    var worker_group = parseInt($('#worker-group').text());
    var final_step = worker_in_group3(worker_group) ? 4 : 5;
    var reset_step = is_final_step(current_step, worker_group) ? 1 : final_step;
    $('#step-value').text(reset_step);

    if (reset_step === 1) {
      localStorage.clear();
      init_step_values();
      localStorage.agreed_to_consent = "true";
      console.log('Reset back to beginning.');
    }

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
    update_steps();
  });

  function update_steps() {
    var current_step = $('#step-value').text();
    var worker_group = parseInt($('#worker-group').text());
    var worker_code = $('#worker-code').text();

    var url = '/naf/update/step';
    var data = {
      'current_step': current_step,
      'is_final_step': is_final_step(current_step, worker_group)
    };

    console.log('data sent: ', data);

    $.post(url, data).done(function(resp) {
      var json_resp = JSON.parse(resp);
      $('#step-value').text(json_resp.next_step);
      $('#span-begin-label').text(get_btn_step_content(json_resp.next_step, worker_group));
      $('#modal-title-value').html(get_modal_title(json_resp.next_step, worker_group));
      $('#modal-body-content').html(get_modal_body(json_resp.next_step, worker_group, worker_code));

      $('#next-step-btn').prop('disabled', true);
      g_video_played = false;

      countdown_next_step_btn(json_resp.next_step, worker_group);
    }).fail(function(error) {
      $('#next-step-btn').prop('disabled', true);
      console.log('step error: ', error);
    });
  }


  function play_started() {
    console.log('user clicked play btn.');
    g_video_played = true;
    var vid = $('video').attr('id');
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    countdown_next_step_btn(current_step, worker_group);
  }

  // function countdown_old_next_step_btn(step) {
  //   $('#next-step-btn').prop('disabled', true);
  //   if (step === 2 || step === 4 || step === 6 || step === 8) {
  //     g_video_played = false;
  //   }
  //
  //   if (g_video_played && (step === 1 || step === 3 || step === 5)) { // videos
  //     do_countdown(65);
  //   }
  //
  //   // survey1 completed
  //   if (step === 2 && localStorage.v1q1 !== "undefined" && localStorage.v1q2 !== "undefined" && localStorage.v1q3 !== "undefined") {
  //     $('#next-step-btn').prop('disabled', false);
  //   }
  //
  //   // survey2 completed
  //   if (step === 4 && localStorage.v2q1 !== "undefined" && localStorage.v2q2 !== "undefined" && localStorage.v2q3 !== "undefined") {
  //     $('#next-step-btn').prop('disabled', false);
  //   }
  //
  //   // survey3 completed
  //   if (step === 6 && localStorage.v3q1 !== "undefined" && localStorage.v3q2 !== "undefined" && localStorage.v3q3 !== "undefined") {
  //     $('#next-step-btn').prop('disabled', false);
  //   }
  //
  //   // demography survey completed
  //   if (step === 7 &&
  //     localStorage.city !== "undefined" && localStorage.city !== "" &&
  //     localStorage.age !== "undefined" && localStorage.age !== "" &&
  //     localStorage.gender !== "undefined" &&
  //     localStorage.education !== "undefined" &&
  //     localStorage.occupation !== "undefined" &&
  //     localStorage.family_size !== "undefined" &&
  //     // family occupation is optional
  //     localStorage.family_income !== "undefined" &&
  //     localStorage.has_mobile !== "undefined" &&
  //     localStorage.watch_video !== "undefined" &&
  //     localStorage.internet_phone !== "undefined") {
  //     $('#next-step-btn').prop('disabled', false);
  //   }
  //
  //   if (step === 8) { // final code
  //     submit_data();
  //     $('#next-step-btn').hide();
  //   }
  // }

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

  function is_final_step(step, worker_group) {
    if (worker_in_group3(worker_group)) {
      return step === 4;
    }
    return step === 5;
  }

  function countdown_next_step_btn(step, worker_group) {
    $('#next-step-btn').prop('disabled', true);
    // g_video_played = false;

    if (step_has_video(step, worker_group) && g_video_played) {
      console.log('countdown step has video');
      do_video_countdown(step, worker_group);
    }

    // main survey completed
    if (is_main_survey_step(step, worker_group) &&
      is_valid(localStorage.mainq1) &&
      is_valid(localStorage.mainq2) &&
      is_valid(localStorage.mainq3) &&
      is_valid(localStorage.mainq4)) {
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

    if (is_final_step(step, worker_group)) { // final code
      $('#next-step-btn').hide();
      if (localStorage.has_successfully_submitted !== "true") {
        submit_data();
      } else {
        console.log('Already successfully submitted data.');
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
        localStorage.has_successfully_submitted = "true";
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
    setTimeout(function() {
      console.log("next button enabled");
      $('#next-step-btn').prop('disabled', false);
    }, seconds * 1000);
  }

  function do_video_countdown(step, worker_group) {
    if (worker_in_group3(worker_group) && step === 1) {
      do_countdown(1);
      console.log('doing countdown for group3 user in step1');
    // do_countdown(167);
    } else if (!worker_in_group3(worker_group) && step === 1) {
      do_countdown(1);
      console.log('doing countdown for NON-group3 user in step1');
    // do_countdown(65);
    } else if (!worker_in_group3(worker_group) && step === 2) {
      console.log('doing countdown for NON-group3 user in step2');
      do_countdown(1);
    // do_countdown(167);
    }
  }

  function get_btn_step_content(step, worker_group) {
    // var contents = "Begin Step " + step;
    var contents = "स्टेप " + step + " को शुरू करें";

    if (is_final_step(step, worker_group)) {
      contents = "Show mturk code";
    }
    return contents;
  }

  // function get_old_modal_body(step, worker_group, worker_code) {
  //   var contents = '';
  //   if (step === 1 || step === 3 || step === 5) {
  //     contents = get_video(step, worker_group);
  //   } else if (step === 2 || step === 4 || step === 6) {
  //     contents = get_survey(step - 1, worker_group);
  //   } else if (step === 7) {
  //     contents = get_demography_survey();
  //   } else if (step === 8) {
  //     // contents = 'Your mturk code: ' + worker_code;
  //     contents = 'आपका MTurk Code  है: ' + worker_code;
  //   }
  //   return contents;
  // }
  //

  function worker_in_group3(worker_group) {
    return worker_group % 3 === 0;
  }

  function get_modal_body(step, worker_group, worker_code) {
    var contents = '';

    if (worker_in_group3(worker_group)) {
      return get_contents_group3(step, worker_group);
    } else {
      return get_contents_group1_group2(step, worker_group);
    }
  }

  function get_contents_group3(step, worker_group) {
    var worker_code;
    var contents;

    if (step === 1) {
      contents = get_video('main.mp4');
    } else if (step === 2) {
      contents = get_main_survey();
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
    var first_video;
    var worker_code;
    var contents;

    if (step === 1) {
      first_video = worker_group % 2 === 0 ? "neg.mp4" : "pos.mp4";
      contents = get_video(first_video);
    } else if (step === 2) {
      contents = get_video('main.mp4');
    } else if (step === 3) {
      contents = get_main_survey();
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
    var total_steps = worker_in_group3(worker_group) ? 4 : 5;

    // var contents = "Step " + step + " of 5";
    var contents = "स्टेप " + step + " / " + total_steps;
    if (step === 8) {
      // contents = "Submit mturk code";
      contents = "अपने MTurk Code को सबमिट करें।";
    }
    return contents;
  }

  function get_video(video_name) {
    var raw_html = '<strong>नीचे दिए हुए वीडियो को ध्यान से fullscreen mode पर देखें।  अपने headphones का इस्तेमाल करें।  यह वीडियो सिर्फ 1 मिनट का है।</strong><br>' +
      '<video width="320" height="240" id="{0}" onplay="naf.play_started()" controls>' +
      '<source src="/static/videos/{0}" type="video/mp4">' +
      'Your browser does not support the video.' +
      '</video>';
    raw_html = raw_html.format(video_name);
    return raw_html;
  }

  // function get_video(step, worker_group) {
  //   var order = get_content_order(step, worker_group);
  //   return get_raw_video(order);
  // }

  // function get_video(step, worker_group) {
  //   var order = get_content_order(step, worker_group);
  //   return get_raw_video(order);
  // }

  //   function get_content_order(step, worker_group) {
  //     step = parseInt(step);
  //     worker_group = parseInt(worker_group);
  //     var video_order = "";
  //     if (worker_group === 1) {
  //       video_order = "1,2,3";
  //     } else if (worker_group === 2) {
  //       video_order = "1,3,2";
  //     } else if (worker_group === 3) {
  //       video_order = "2,1,3";
  //     } else if (worker_group === 4) {
  //       video_order = "2,3,1";
  //     } else if (worker_group === 5) {
  //       video_order = "3,1,2";
  //     } else if (worker_group === 6) {
  //       video_order = "3,2,1";
  //     }
  //     video_order = video_order.split(',');
  //
  //     var order;
  //     if (step === 1) {
  //       order = video_order[0];
  //     } else if (step === 3) {
  //       order = video_order[1];
  //     } else if (step === 5) {
  //       order = video_order[2];
  //     }
  //     return parseInt(order);
  //   }

  // function get_raw_video(order) {
  //   var mp4 = 'v' + order + '.mp4';
  //   // var raw_html = '<strong>Watch in fullscreen mode and use headphones.</strong>' +
  //   //   '<video width="320" height="240" id="{0}" onplay="naf.play_started()" controls>' +
  //   //   '<source src="/static/videos/{0}" type="video/mp4">' +
  //   //   'Your browser does not support the video.' +
  //   //   '</video>';
  //
  //   var raw_html = '<strong>नीचे दिए हुए वीडियो को ध्यान से fullscreen mode पर देखें।  अपने headphones का इस्तेमाल करें।  यह वीडियो सिर्फ 1 मिनट का है।</strong><br>' +
  //     '<video width="320" height="240" id="{0}" onplay="naf.play_started()" controls>' +
  //     '<source src="/static/videos/{0}" type="video/mp4">' +
  //     'Your browser does not support the video.' +
  //     '</video>';
  //   raw_html = raw_html.format(mp4);
  //   return raw_html;
  // }

  // function get_survey(step, worker_group) {
  //   var order = get_content_order(step, worker_group);
  //   var vid;
  //   if (step === 1) {
  //     vid = 'v1';
  //   } else if (step === 3) {
  //     vid = 'v2';
  //   } else if (step === 5) {
  //     vid = 'v3';
  //   }
  //
  //   var form = '<form onclick="check_old_video_survey()">' +
  //     '<div class="form-group">' +
  //     // '<label for="">Using the image below, indicate how happy or sad you feel after watching the video. Please tick the figure that best represents your feelings. </label>' +
  //     '<label for="">आपको यह वीडियो  देखने के बाद कितनी खुशी या दुख हुआ? कृप्या उस निशान को चुने जो आपके मन के भाव  को सबसे अच्छे से बताता हो।</label>' +
  //     '<img src="/static/images/naf/valence.png" width="550px" height="150px" alt="valence image" />' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q1" value="1"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q1" value="2"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q1" value="3"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q1" value="4"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q1" value="5"/>' +
  //     '</label>' +
  //     '</div>' +
  //     '<br/>' +
  //     '<br/>' +
  //     '<div class="form-group">' +
  //     // '<label for="">Using the image below, please indicate how the video affects you. Select the figure that best represents your feelings.</label>' +
  //     '<label for="">आपको यह वीडियो  देखने के बाद कितना फर्क पड़ा ? कृप्या उस निशान को चुने जो आपके मन के भाव  को सबसे अच्छे से बताता हो। </label>' +
  //     '<img src="/static/images/naf/arousal.png" width="550px" height="150px" alt="arousal image" />' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q2" value="1"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q2" value="2"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q2" value="3"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q2" value="4"/>' +
  //     '</label>' +
  //     '<label class="naf-radio">' +
  //     '<input type="radio" name="{0}q2" value="5"/>' +
  //     '</label>' +
  //     '</div>' +
  //     '<br/>' +
  //     '<br/>' +
  //     '<div class="form-group">' +
  //     // '<label for="">What was the topic of the video?</label>' +
  //     '<label for="">यह वीडियो किस विषय पर था ?</label>' +
  //     '<br>' +
  //     '<span>' +
  //     // '<input type="radio" name="{0}q3" value="1"/> Nutrition of newborn' +
  //     '<input type="radio" name="{0}q3" value="1"/> नवजात बच्चे के पोषण के बारे में' +
  //     '</span>' +
  //     '<br>' +
  //     '<span>' +
  //     // '<input type="radio" name="{0}q3" value="2"/> Dangerous effects of smoking and tobacco' +
  //     '<input type="radio" name="{0}q3" value="2"/> धूम्रपान करने के और तम्बाकू खाने के नुकसान' +
  //     '</span>' +
  //     '<br>' +
  //     '<span>' +
  //     // '<input type="radio" name="{0}q3" value="3"/> Importance of washing hands' +
  //     '<input type="radio" name="{0}q3" value="3"/> हाथों को अच्छे से साफ़ करने के बारे में' +
  //     '</span>' +
  //     '<br>' +
  //     '<span>' +
  //     // '<input type="radio" name="{0}q3" value="4"/> Safe drinking water' +
  //     '<input type="radio" name="{0}q3" value="4"/> स्वच्छ जल को पीने के बारे में' +
  //     '</span>' +
  //     '<br>' +
  //     '<span>' +
  //     // '<input type="radio" name="{0}q3" value="5"/> Treatment of Diarrhea' +
  //     '<input type="radio" name="{0}q3" value="5"/> दस्त के इलाज के बारे में' +
  //     '</span>' +
  //     '<br>' +
  //     '<span>' +
  //     // '<input type="radio" name="{0}q3" value="5"/> None of these' +
  //     '<input type="radio" name="{0}q3" value="5"/> इनमे से कोई नहीं' +
  //     '</span>' +
  //     '</div>' +
  //     '</form>';
  //
  //   form = form.format(vid);
  //   return form;
  // }

  function get_main_survey() {
    var vid = "main";
    var form = '<form onchange="naf.check_main_survey()">' +
      '<div class="form-group">' +
      // '<label for="">Using the image below, indicate how happy or sad you feel after watching the video. Please tick the figure that best represents your feelings. </label>' +
      '<label for="">How much did you like the last video?</label>' +
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
      '<label for="">How useful was the last video to you?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="1"/> Highly non-useful' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="2"/> Slightly non-useful ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="3"/> Neutral' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="4"/> Slightly useful' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q2" value="5"/> Highly useful' +
      '</span>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      '<label for="">How entertaining was the last video to you?</label>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="1"/> Highly unentertaining' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="2"/> Slightly unentertaining ' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="3"/> Neutral' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="4"/> Slightly enteraining' +
      '</span>' +
      '<br>' +
      '<span>' +
      '<input type="radio" name="{0}q3" value="5"/> Highly enteraining' +
      '</span>' +
      '</div>' +
      '<br/>' +
      '<br/>' +
      '<div class="form-group">' +
      '<label>How can the last video be improved?</label>' +
      '<input type="textarea" class="form-control" id="{0}q4" max=50 placeholder="type response here">' +
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
    localStorage.mainq4 = $('#mainq4').val();

    if (is_valid(localStorage.mainq1) &&
      is_valid(localStorage.mainq2) &&
      is_valid(localStorage.mainq3) &&
      is_valid(localStorage.mainq4)) {
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


  function init_step_values() {
    var current_step = parseInt($('#step-value').text());
    var worker_group = parseInt($('#worker-group').text());
    var worker_code = $('#worker-code').text();
    $('#span-begin-label').text(get_btn_step_content(current_step, worker_group));
    $('#modal-title-value').html(get_modal_title(current_step, worker_group));
    $('#modal-body-content').html(get_modal_body(current_step, worker_group, worker_code));
    countdown_next_step_btn(current_step, worker_group);
  }
  init_step_values();

  function current_worker_in_group3() {
    var worker_group = parseInt($('#worker-group').text());
    return worker_in_group3(worker_group);
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

// function check_demogr() {
//   console.log('oncick demogr called');
//   checkSurvey('demography');
// }

// function checkSurvey(name) {
//   // survey1
//   if (name === 'v1') {
//     console.log('completing v1 survey');
//     localStorage.v1q1 = $('input[name=v1q1]:checked').val();
//     localStorage.v1q2 = $('input[name=v1q2]:checked').val();
//     localStorage.v1q3 = $('input[name=v1q3]:checked').val();
//     console.log(localStorage.v1q1, localStorage.v1q2, localStorage.v1q3);
//
//     if (localStorage.v1q1 !== "undefined" && localStorage.v1q2 !== "undefined" && localStorage.v1q3 !== "undefined") {
//       $('#next-step-btn').prop('disabled', false);
//       console.log('Will enable next button for step 3.');
//     }
//   }
//
//   // survey2
//   else if (name === 'v2') {
//     console.log('completing v2 survey');
//     localStorage.v2q1 = $('input[name=v2q1]:checked').val();
//     localStorage.v2q2 = $('input[name=v2q2]:checked').val();
//     localStorage.v2q3 = $('input[name=v2q3]:checked').val();
//     console.log(localStorage.v2q1, localStorage.v2q2, localStorage.v2q3);
//
//     if (localStorage.v2q1 !== "undefined" && localStorage.v2q2 !== "undefined" && localStorage.v2q3 !== "undefined") {
//       $('#next-step-btn').prop('disabled', false);
//       console.log('Will enable next button for step 5.');
//     }
//   }
//
//   // survey3
//   else if (name === 'v3') {
//     console.log('completing v3 survey');
//     localStorage.v3q1 = $('input[name=v3q1]:checked').val();
//     localStorage.v3q2 = $('input[name=v3q2]:checked').val();
//     localStorage.v3q3 = $('input[name=v3q3]:checked').val();
//     console.log(localStorage.v3q1, localStorage.v3q2, localStorage.v3q3);
//
//     if (localStorage.v3q1 !== "undefined" && localStorage.v3q2 !== "undefined" && localStorage.v3q3 !== "undefined") {
//       $('#next-step-btn').prop('disabled', false);
//       console.log('Will enable next button for step 7.');
//     }
//   }
//
//   // demography
//   else if (name === 'demography') {
//     console.log('demography called!', localStorage);
//     localStorage.city = $('#demogr-city').val();
//     localStorage.age = $('#demogr-age').val();
//     localStorage.gender = $('input[name=demogr-gender]:checked').val();
//     localStorage.education = $('input[name=demogr-education]:checked').val();
//     localStorage.occupation = $('#demogr-occupation').val();
//     localStorage.family_size = $('#demogr-family-size').val();
//     localStorage.family_occupation = $('#demogr-family-occupation').val();
//     localStorage.family_income = $('#demogr-family-income').val();
//     localStorage.has_mobile = $('input[name=demogr-has-mobile]:checked').val();
//     localStorage.watch_video = $('input[name=demogr-watch-video]:checked').val();
//     localStorage.internet_phone = $('input[name=demogr-internet-phone]:checked').val();
//
//     if (localStorage.city !== "undefined" &&
//       localStorage.age !== "undefined" &&
//       localStorage.gender !== "undefined" &&
//       localStorage.education !== "undefined" &&
//       localStorage.occupation !== "undefined" &&
//       localStorage.family_size !== "undefined" &&
//       // family occupation is optional
//       localStorage.family_income !== "undefined" &&
//       localStorage.has_mobile !== "undefined" &&
//       localStorage.watch_video !== "undefined" &&
//       localStorage.internet_phone !== "undefined") {
//       $('#next-step-btn').prop('disabled', false);
//     }
//
//   }
// }
