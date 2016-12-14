////////////////////////////////////////////////
// rep.js
////////////////////////////////////////////////

$(document).ready(function() {

  // enable string formatting: '{0}{1}'.format(var1, var2)
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/\{(\d+)\}/g, function(m, n) {
      return args[n];
    });
  };

  // fetch param from url: xyz.com?enable=yes ---> urlParam(enable) returns yes
  $.url_param = function(name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results === null) {
      return null;
    } else {
      return results[1] || 0;
    }
  };

  var errors = {
    'internal_server_error': 'oops, cannot complete request at this time. contact admin.',
    'method_not_allowed': 'profile update failed. try again later or contact admin.'
  };

  ////////////////////////////////////////////////
  // helper functions
  ////////////////////////////////////////////////
  function disable(btn_id) {
    $(btn_id).prop("disabled", true);
  }

  function enable(btn_id) {
    $(btn_id).prop("disabled", false);
  }

  function show_busy_div(div) {
    $(div).html('Processing...').css('color', 'orange');
  }

  function show_success_msg(div, msg) {
    $(div).html(msg).css('color', 'green');
  }

  function show_plain_msg(div, msg) {
    $(div).html(msg).css('color', 'black');
  }

  function show_error_msg(div, msg) {
    $(div).html(msg).css('color', 'red');
  }


  function submit_checkbox_val(field, input) {
    var url = 'settings/tracking/' + field + '/' + input;
    var response_field = '#' + field + '-checkbox-status';

    $.get(url, function(resp) {
      var results = JSON.parse(resp);
      console.log('results: ', results);
    }).fail(function(error) {
      show_error_msg(response_field, errors.internal_server_error);
    });
  }


  ////////////////////////////////////////////////
  // authenticate/connect data streams
  ////////////////////////////////////////////////
  $('#signin-btn').click(function() {
    window.location.href = '/google_login';
  });

  $('#mturk-auth-moves-btn').click(function() {

    if ($('#mturk-worker-id').val() === '') {
      show_error_msg('#mturk-submit-status', 'Submit a valid worker id before you connect Moves app.');
      return;
    }
    window.location.href = '/mturk-auth-moves';
  });

  $('#auth-moves-btn').click(function() {
    $('#auth-status-div').html('connecting to moves...');
    window.location.href = '/auth-moves';
  });

  $('#auth-pam-btn').click(function() {
    window.location.href = '/auth-pam';
  });

  $('#auth-rt-btn').click(function() {
    window.location.href = '/auth-rt';
  });


  ////////////////////////////////////////////////
  // checkboxes for activating datastreams
  ////////////////////////////////////////////////
  $('#location-checkbox-btn').on('change', function() {
    submit_checkbox_val('location', this.checked);
  });

  $('#mood-checkbox-btn').on('change', function() {
    submit_checkbox_val('mood', this.checked);
  });

  $('#sn-checkbox-btn').on('change', function() {
    submit_checkbox_val('sn', this.checked);
  });


  ////////////////////////////////////////////////
  // dropdowns
  ////////////////////////////////////////////////

  $('#dropdown-action li').on('click', function() {
    var selected = $(this).text();
    $('#dropdown-action-label').html(selected);
  });

  $('#dropdown-calendar li').on('click', function() {
    var selected = $(this).text();
    $('#dropdown-cal-label').html(selected);
  });

  $('#dropdown-cmd li').on('click', function() {
    var selected = $(this).text();
    $('#dropdown-cmd-label').html(selected);
  });

  $('#execute-config-btn').click(function() {
    var calendar_selected = $('#dropdown-cal-label').text().replace(/\s/g, ''); // regex removes all spaces in string
    var command_selected = $('#dropdown-cmd-label').text().replace(/\s/g, ''); // regex removes all spaces in string
    var response_field = '#execute-config-status';

    // if (calendar_selected === 'ChooseDatastream' || command_selected === 'ChoooseCommand') {
    if (calendar_selected.indexOf('Choose') >= 0 || command_selected.indexOf('ChoooseCommand') >= 0) {
      show_error_msg(response_field, 'Both entries must be selected from dropdown menu.');
      return;
    }

    var url = '/settings/execute/' + calendar_selected + '/' + command_selected;
    show_busy_div(response_field);

    $.get(url, function(resp) {
      show_success_msg(response_field, resp);
    }).fail(function(error) {
      show_error_msg(response_field, errors.internal_server_error);
    });
  });

  ////////////////////////////////////////////////
  // other buttons
  ////////////////////////////////////////////////

  var gen_code = $.url_param('gen_code');
  if (gen_code) {
    localStorage.gen_code = gen_code;
  }
  var gen_txt = localStorage.gen_code ?
    '<strong>' + localStorage.gen_code + '</strong>' :
    '(<em>no code yet<em/>).';
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

    var url = '/mturk/worker_id';
    var data = {
      'worker_id': worker_id
    };

    $.post(url, data).done(function(resp) {
      localStorage.worker_id = worker_id;
      show_success_msg(response_field, 'Successfully submitted worker id.');
    }).fail(function(error) {
      var msg = 'Submission error. Pls contact MTurk Requester (Error: {0} / {1}).'.format(error.status,
        error.statusText);
      show_error_msg(response_field, msg);
    });

  });


  ////////////////////////////////////////////////
  // experiment and intervention functions
  ////////////////////////////////////////////////
  $('#create-experiment-btn').click(function(event) {
    event.preventDefault();
    var title = $('#experiment-title-id').val();
    var rescuetime = $('#rescuetime-checkbox-btn').is(':checked');
    var aware = $('#aware-checkbox-btn').is(':checked');
    var geofence = $('#geofence-checkbox-btn').is(':checked');
    var text = $('#text-checkbox-btn').is(':checked');
    var image = $('#image-checkbox-btn').is(':checked');
    var reminder = $('#reminder-checkbox-btn').is(':checked');
    var actuators = $('#actuators-checkbox-btn').is(':checked');
    var response_field = '#create-experiment-status';

    console.log(rescuetime, aware, geofence);

    if (title === '') {
      show_error_msg(response_field, 'You need to add a title for your experiment.');
      return;
    }

    $('#add-experiment-modal').modal('hide');

    var url = '/add/experiment';
    var data = {
      'title': title,
      'rescuetime': rescuetime,
      'aware': aware,
      'geofence': geofence,
      'text': text,
      'image': image,
      'reminder': reminder,
      'actuators': actuators
    };

    $.post(url, data).done(function(resp) {
      show_success_msg(response_field, resp);
      update_experiment_view();
    }).fail(function(error) {
      show_error_msg(response_field, error);
    });

  });

  update_experiment_view();

  function update_experiment_view() {
    var view, exp, row, response_field;
    response_field = '#experiment-view-status';

    $.get('/fetch/experiments', function(results) {
      var experiments = JSON.parse(results);
      var view = create_experiment_view(experiments);
      $('#experiment-view-id').html(view);
    }).fail(function(error) {
      show_error_msg(response_field, 'Could not load experiment view.');
      console.warn(error);
    });
  }

  function create_experiment_view(experiments) {
    view = '<table id="exp-view-id" class="table table-striped table-bordered"><tr>' +
      '<th> Title </th>' +
      '<th> Code </th>' +
      '<th> RescueTime </th>' +
      '<th> Aware </th>' +
      '<th> Geofence </th>' +
      '<th> Text </th>' +
      '<th> Image </th>' +
      '<th> Reminder </th>' +
      '<th> Actuators </th>' +
      '</tr><tbody>';

    // show css background class for cell to provide visual effect for enable/disable buttons
    var rescuetime_c, aware_c, geofence_c, text_c, image_c, reminder_c, actuators_c;

    for (var i = experiments.length - 1; i >= 0; i--) {
      exp = experiments[i];

      rescuetime_c = exp.rescuetime ? 'success' : 'danger';
      aware_c = exp.aware ? 'success' : 'danger';
      geofence_c = exp.geofence ? 'success' : 'danger';
      text_c = exp.text ? 'success' : 'danger';
      image_c = exp.image ? 'success' : 'danger';
      reminder_c = exp.reminder ? 'success' : 'danger';
      actuators_c = exp.actuators ? 'success' : 'danger';

      row = '<tr>' +
        '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code) +
        '<td>' + exp.code + '</td>' +
        '<td class={0}> {1} </td>'.format(rescuetime_c, exp.rescuetime) +
        '<td class={0}> {1} </td>'.format(aware_c, exp.aware) +
        '<td class={0}> {1} </td>'.format(geofence_c, exp.geofence) +
        '<td class={0}> {1} </td>'.format(text_c, exp.text) +
        '<td class={0}> {1} </td>'.format(image_c, exp.image) +
        '<td class={0}> {1} </td>'.format(reminder_c, exp.reminder) +
        '<td class={0}> {1} </td>'.format(actuators_c, exp.actuators) +
        '</tr>';

      view += row;
    }

    view += '</tbody></table>';
    return view;
  }



  /////////////////////////////
  // edit / delete experiment
  /////////////////////////////
  $(document).on('click', '#exp-view-id .btn-link', function() {
    var code = this.id;
    window.location.href = '/edit-experiment/{0}'.format(code);
  });

  $('#go-back-btn').click(function() {
    window.location.href = '/researcher_login';
  });

  $('#save-single-experiment-btn').click(function() {
    var title = $('#edit-exp-title').val();
    var code = $('#save-single-experiment-btn').val();
    var rescuetime = $('#edit-rescuetime-checkbox-btn').is(':checked');
    var aware = $('#edit-aware-checkbox-btn').is(':checked');
    var geofence = $('#edit-geofence-checkbox-btn').is(':checked');
    var text = $('#edit-text-checkbox-btn').is(':checked');
    var image = $('#edit-image-checkbox-btn').is(':checked');
    var reminder = $('#edit-reminder-checkbox-btn').is(':checked');
    var actuators = $('#edit-actuators-checkbox-btn').is(':checked');
    var response_field = '#edit-experiment-status';

    if (title === '') {
      show_error_msg(response_field, 'You need to add a title for your experiment.');
      return;
    }

    var url = '/update/experiment';
    var data = {
      'title': title,
      'code': code,
      'rescuetime': rescuetime,
      'aware': aware,
      'geofence': geofence,
      'text': text,
      'image': image,
      'reminder': reminder,
      'actuators': actuators
    };

    $.post(url, data).done(function(resp) {
      show_success_msg(response_field, 'Experiment successfully updated. Refreshing title...');
      window.location.href = window.location.href;
    }).fail(function(error) {
      show_error_msg(response_field, error);
    });

  });

  $('#delete-single-experiment-btn').click(function() {
    if (confirm("Are you sure you want to delete this experiment permanently?") === true) {
      var code = $('#delete-single-experiment-btn').val();
      window.location.href = '/delete/experiment/{0}'.format(code);
    }
  });


  /////////////////////////////
  // upload images and texts
  /////////////////////////////
  $('#upload-image-text-btn').click(function(event) {
    console.log('image text clicked');
    event.preventDefault();

    var image = $('#image').get(0).files[0];
    var txt = $('#txt').val();
    var response_field = '#upload-image-text-status';

    if (!image && !txt) {
      show_error_msg(response_field, 'You need to add either an image or a text.');
      return;
    }

    var formData = new FormData();
    formData.append('text', txt);
    formData.append('image', image);

    var image_name = image ? image.name : '';
    formData.append('image_name', image_name);

    $.ajax({
      url: '/add/image_text',
      success: function(e) {
        console.log('resp: ', e);
        show_success_msg(response_field, 'Image successfully uploaded.');
        // $('#fetch-all-imgs-btn').click();
      },
      error: function(e) {
        show_error_msg(response_field, 'Image upload error. Pls contact admin.');
      },
      complete: function(e) {
        setTimeout(function() {
          $('#upload-image-modal').modal('hide');
          show_plain_msg(response_field, '');
          $('#image').val('');
          window.location.href = window.location.href;
        }, 1000);
      },
      data: formData,
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false
    });
    return false;
  });


  /////////////////////////////
  // create intervention table
  /////////////////////////////
  create_new_intv_table();

  function create_new_intv_table() {

    var view, no_of_groups, participants, other_headers, group_rows, row;

    participants = $('#ps-per-group').val();
    $('#ps-prompt').html("<em>randomized participants per group: {0} </em>".format(participants));

    no_of_groups = parseInt($('#no-of-groups').val());
    other_headers = 4;

    group_rows = '';
    for (var i = 0; i < no_of_groups; i++) {
      group_rows += '<th class="col-md-1"> Group{0} </th>'.format(i + 1);
    }

    view = '<table id="intvn-table-id" class="table table-striped table-bordered table-hover"><tr>' + group_rows +
      '<th class=col-md-1> Start </th>' +
      '<th class="col-md-1"> Every </th>' +
      '<th class="col-md-1"> When </th>' +
      '<th class="col-md-1"> Repeat </th>' +
      '</tr><tbody></tbody></table>';

    $('#intv-table-view').html(view);
  }

  add_intv_row();

  function add_intv_row() {
    var no_of_groups, group_rows, new_row, img_text_options;

    no_of_groups = parseInt($('#no-of-groups').val());
    group_rows = '';

    $.get('/fetch/images').done(function(img_resp) {
      $.get('/fetch/texts').done(function(text_resp) {

        img_text_options = create_img_text_options(img_resp, text_resp);

        for (var j = 0; j < no_of_groups; j++) {
          group_rows += '<td>{0}</td>'.format(img_text_options);
        }

        var date_input = '<input class="form-control" id="intv-start-date" data-provide="datepicker"' +
          'data-date-start-date="+0d"' +
          'data-date-format="yyyy-mm-dd"' +
          'data-date-today-highlight=true' +
          'placeholder="select start date" value="2016-12-30">';

        new_row = '<tr class="del-row">' + group_rows +
          '<td> {0} </td>'.format(date_input) +
          '<td> {0} </td>'.format(create_every_options()) +
          '<td> <input type="time" class="form-control" id="intv-time" value="00:00:00.000"/> </td>' +
          '<td> <input type="number" id="intv-repeat" class="form-control" style="width: 80px" min=1 value=1 /> </td>' +
          '</tr>';

        $('#intvn-table-id').append(new_row);

      });
    });
  }

  function create_every_options() {
    var options = '<select id="intv-every" class="form-control">' +
      ' <optgroup label="Daily">' +
      ' <option>Day</option> ' +
      ' </optgroup>' +
      ' <optgroup label="Once per Week">' +
      ' <option>Mon</option> ' +
      ' <option>Tues</option> ' +
      ' <option>Wed</option> ' +
      ' <option>Thurs</option> ' +
      ' <option>Fri</option> ' +
      ' <option>Sat</option> ' +
      ' <option>Sun</option> ' +
      ' </optgroup>' +
      ' </select>';
    return options;
  }

  function create_img_text_options(img_resp, text_resp) {
    var i, images, texts, image_options, text_options;

    images = JSON.parse(img_resp);
    texts = JSON.parse(text_resp);

    image_options = '';
    for (i = 0; i < images.length; i++) {
      var img = images[i];
      image_options += '<option value="{0}">{1}</option>'.format(img.image_url, img.image_name);
    }

    text_options = '';
    for (i = 0; i < texts.length; i++) {
      var txt = texts[i];
      text_options += '<option>{0}</option>'.format(txt.text);
    }

    var options = '<select id="intv-img-text" class="form-control">' +
      ' <optgroup label="Texts">' + text_options +
      ' </optgroup>' +
      ' <optgroup label="Images">' + image_options +
      ' </optgroup>' +
      ' </select>';

    return options;
  }

  $('#add-row-btn').click(function() {
    add_intv_row();
  });

  $('#remove-row-btn').click(function() {
    $('#intvn-table-id tr:last').remove();
  });

  $('#delete-table-btn').click(function() {
    create_new_intv_table();
  });

  $('#update-table-btn').click(function() {
    create_new_intv_table();
    add_intv_row();

    var ps_per_group = $('#ps-per-group').val();
    $('#randomized-group-status').html("<em>Randomized participants per group: {0} </em>".format(ps_per_group));
  });


  $('#save-table-btn').click(function() {

    var ps_per_group = $('#ps-per-group').val();
    $('#randomized-group-status').html("<em>Randomized participants per group: {0} </em>".format(ps_per_group));

    var no_of_groups = parseInt($('#no-of-groups').val());
    console.log('no of groups: ', no_of_groups);

    var intv_img_text = $('#intv-img-text').val();
    console.log('intv_img_text:', intv_img_text);

    var intv_start_date = $('#intv-start-date').val();
    console.log('intv_start_date : ', intv_start_date);

    var intv_every = $('#intv-every').val();
    console.log('intv_every:', intv_every);

    var intv_time = $('#intv-time').val();
    console.log('intv_time:', intv_time);

    var intv_repeat = $('#intv-repeat').val();
    console.log('intv_repeat:', intv_repeat);

    var exp_code = $('#save-single-experiment-btn').val(); // code hidden in button
    console.log('exp_code:', exp_code);

    var response_field = '#intv-table-status';
    var url = '/add/intervention';
    var data = {
      'group': intv_img_text,
      'code': exp_code,
      'start': intv_start_date,
      'every': intv_every,
      'when': intv_time,
      'repeat': intv_repeat
    };

    $.post(url, data).done(function(resp) {
      show_success_msg(response_field, 'Intervention successfully saved.');
      console.log('added intv resp: ', resp);

      setTimeout(function() {
        window.location.href = window.location.href;
      }, 1000);

    }).fail(function(error) {
      show_error_msg(response_field, 'Error saving intervention.');
      console.log('intv save error:', error);
    });

  });


  // reset all previous entries
  $('#reset-btn').click(function() {

    var r = confirm(
      "Are you sure about resetting calendar? Everything will be wiped out."
    );
    if (r) {
      $('#cal-status-div').html('Resetting calendar...');
      $.get('/settings/reset', function(resp) {
        $('#cal-status-div').html(resp);
      });
    } else {
      $('#cal-status-div').html('');
    }
  });

  $('#change-btn').click(function() {
    var r = confirm(
      "Are you sure about changing calendar? Current data will be discarded."
    );
    if (r) {
      $('#cal-status-div').html('Changing calendar...');
      $.get('/settings/change', function(resp) {
        $('#cal-status-div').html(resp);
        window.location.href = '/auth-gcal';
      });
    } else {
      $('#cal-status-div').html('');
    }
  });

  // delete location calendar
  $('#delete-btn').click(function() {
    var r = confirm(
      "Are you sure you want to completely remove calendar?");
    if (r) {
      $('#cal-status-div').html('deleting SLM-Location calendar...');
      $.get('/settings/delete', function(resp) {
        $('#cal-status-div').html(resp);
      });
    } else {
      $('#cal-status-div').html('');
    }
  });

  $('#moves-export-btn').click(function() {

    var response_field = '#moves-status-div';
    var date_str = $('#loc-date').val();
    var yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);

    var request;

    if (date_str === '') {
      date_str = yesterday.toJSON().slice(0, 10);
      $('#loc-date').val(date_str);
    }

    url = '/data-moves/' + date_str;
    $('#moves-status-div').html('Exporting moves data for ' + date_str + '...');

    $.get(url, function(resp) {
      var response_field = '#moves-status-div';

      if (typeof(resp) === 'string') {
        show_success_msg(response_field, resp);
        return;
      }

      var result = JSON.parse(resp);
      result = typeof(result) !== 'object' ? JSON.parse(result) : result;

      if ('error' in result) {
        show_error_msg(response_field, 'Error: ' + result.error);
        return;
      }

      if (result.length < 1) {
        $('#moves-status-div').html();
        show_error_msg(response_field, 'No data available.');
        return;
      }

      show_success_msg('#moves-status-div', resp);

    }).fail(function(error) {
      show_error_msg(response_field, errors.internal_server_error);
    });

  });

  $('#pam-export-btn').click(function() {

    var response_field = '#pam-status-div';
    var date_str = $('#pam-date').val();
    var yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    var request;

    if (date_str === '') {
      date_str = yesterday.toJSON().slice(0, 10);
      $('#pam-date').val(date_str);
    }

    url = '/data-pam/' + date_str;
    $(response_field).html('Exporting PAM data for ' + date_str + '...');

    $.get(url, function(resp) {
      var response_field = '#pam-status-div';

      if (typeof(resp) === 'string') {
        show_success_msg(response_field, resp);
        return;
      }

      var result = JSON.parse(resp);
      console.log('response: ', result);

      if ('error' in result) {
        show_error_msg(response_field, 'Error: ' + result.error);
        return;
      }

      if (result.length < 1) {
        show_error_msg(response_field, 'No data available.');
        return;
      }

      show_success_msg(response_field, resp);

    }).fail(function(error) {
      show_error_msg(response_field, errors.internal_server_error);
    });

  });


  $('#rt-export-btn').click(function() {

    var response_field = '#rt-status-div';
    var date_str = $('#rt-date').val();
    var yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    var request;

    if (date_str === '') {
      date_str = yesterday.toJSON().slice(0, 10);
      $('#rt-date').val(date_str);
    }

    url = '/data-rt/' + date_str;
    $(response_field).html('Exporting RescueTime data for ' + date_str + '...');

    $.get(url, function(resp) {
      var response_field = '#rt-status-div';

      if (typeof(resp) === 'string') {
        show_success_msg(response_field, resp);
        return;
      }

      var result = JSON.parse(resp);
      console.log('result: ', result);

      var printout;
      var tmp = result.row_headers.join(',&#09;&#09;&#09;'); // &#09 is tab
      printout = '<b>' + tmp + '</b><br>';

      result.rows.forEach(function(row) {
        tmp = row.join(',&#09;&#09;&#09;');
        printout += tmp + '<br>';
      });

      if (resp.length < 1) {
        show_error_msg(response_field, 'No data available.');
        return;
      }

      show_success_msg(response_field, printout);

    }).fail(function(error) {
      show_error_msg(response_field, errors.internal_server_error);
    });

  });

  // #################################################
  // update profile fields
  // #################################################
  $('#update-profile-btn').click(function() {
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
      'gender': gender,
    };

    $.post(url, data).done(function(resp) {
      show_success_msg('#update-profile-status', 'profile successfully updated');
    }).fail(function(error) {
      show_error_msg('#update-profile-status', errors.method_not_allowed);
    });

  });

  // #################################################
  // page animation for message
  // #################################################
  $(".alert-dismissible").each(function(index) {
    var $me = $(this);
    $me.delay(2000 + 800 * index).fadeTo(200, 0).slideUp(200,
      function() {
        $me.alert('close');
      });
  });

}); // (document).ready
