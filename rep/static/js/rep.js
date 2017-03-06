////////////////////////////////////////////////
// rep.js
////////////////////////////////////////////////

function hip() {
  alert('hip');
}

// add date range values for experiment start and end dates
$('.input-daterange input').each(function() {
  $(this).datepicker('clearDates');
});

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

// var gen_code = $.url_param('gen_code');
// if (gen_code) {
//   localStorage.gen_code = gen_code;
// }
// var gen_txt = localStorage.gen_code ? '<strong>' + localStorage.gen_code + '</strong>' : '(<em>no code yet<em/>).';
// $('#gen-code-id').html(gen_txt);
// $('#mturk-worker-id').val(localStorage.worker_id);
//
// $('#mturk-submit-btn').click(function(event) {
//   event.preventDefault();
//
//   var worker_id = $('#mturk-worker-id').val();
//   worker_id = worker_id.replace(/[^a-z0-9\s]/gi, '');
//   var response_field = '#mturk-submit-status';
//
//   if (worker_id === '') {
//     show_error_msg(response_field, 'Please submit a valid worker id.');
//     return;
//   }
//
//   var url = '/mturk/worker_id';
//   var data = {
//     'worker_id': worker_id
//   };
//
//   $.post(url, data).done(function(resp) {
//     localStorage.worker_id = worker_id;
//     show_success_msg(response_field, 'Successfully submitted worker id.');
//   }).fail(function(error) {
//     var msg = 'Submission error. Pls contact MTurk Requester (Error: {0} / {1}).'.format(error.status, error.statusText);
//     show_error_msg(response_field, msg);
//   });
//
// });

////////////////////////////////////////////////
// experiment and intervention functions
////////////////////////////////////////////////
$('#create-experiment-btn').click(function(event) {
  event.preventDefault();
  var title = $('#experiment-title-id').val();
  var start = $('#exp-start-date').val();
  var end = $('#exp-end-date').val();
  var rescuetime = $('#rescuetime-checkbox-btn').is(':checked');
  // var image = $('#text-checkbox-btn').is(':checked');
  // var text = $('#image-checkbox-btn').is(':checked');
  var dashboard = $('#dashboard-checkbox-btn').is(':checked');
  var calendar = $('#calendar-checkbox-btn').is(':checked');
  var geofence = $('#geofence-checkbox-btn').is(':checked');
  var reminder = $('#reminder-checkbox-btn').is(':checked');
  var actuators = $('#actuators-checkbox-btn').is(':checked');
  var response_field = '#create-experiment-status';

  if (title === '') {
    show_error_msg(response_field, 'You need to add a title for your experiment.');
    return;
  }

  if (start === '' || end === '') {
    show_error_msg(response_field, 'Experiment start and end dates needed.');
    return;
  }

  var exp_start_datetime = '{0}T00:00:00-05:00'.format(start);
  exp_start_datetime = new Date(exp_start_datetime);

  var exp_end_datetime = '{0}T00:00:00-05:00'.format(end);
  exp_end_datetime = new Date(exp_end_datetime);

  if (exp_start_datetime.getTime() > exp_end_datetime.getTime()) {
    show_error_msg(response_field, 'Start date must come before end date.');
    return;
  }

  var url = '/add/experiment';
  var data = {
    'title': title,
    'start': exp_start_datetime.toJSON(),
    'end': exp_end_datetime.toJSON(),
    'rescuetime': rescuetime,
    'calendar': calendar,
    'geofence': geofence,
    'text': dashboard === true,
    'image': dashboard === true,
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
  var view,
    exp,
    row,
    response_field;
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
  var rescuetime_c,
    calendar_c,
    geofence_c,
    text_c,
    image_c,
    reminder_c,
    actuators_c;

  for (var i = experiments.length - 1; i >= 0; i--) {
    exp = experiments[i];

    rescuetime_c = exp.rescuetime ? 'success' : 'danger';
    calendar_c = exp.calendar ? 'success' : 'danger';
    geofence_c = exp.geofence ? 'success' : 'danger';
    text_c = exp.text ? 'success' : 'danger';
    image_c = exp.image ? 'success' : 'danger';
    reminder_c = exp.reminder ? 'success' : 'danger';
    actuators_c = exp.actuators ? 'success' : 'danger';

    row = '<tr>' +
      '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code) + '<td>' + exp.code + '</td>' + '<td class={0}> {1} </td>'.format(rescuetime_c, exp.rescuetime) + '<td class={0}> {1} </td>'.format(calendar_c, exp.calendar) + '<td class={0}> {1} </td>'.format(geofence_c, exp.geofence) + '<td class={0}> {1} </td>'.format(text_c, exp.text) + '<td class={0}> {1} </td>'.format(image_c, exp.image) + '<td class={0}> {1} </td>'.format(reminder_c, exp.reminder) + '<td class={0}> {1} </td>'.format(actuators_c, exp.actuators) + '</tr>';

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
  console.log('go back clicked');
  window.location.href = '/researcher_login';
});

$('#update-experiment-btn').click(function() {
  var code = $('#code_from_hidden_element').val();
  var title = $('#edit-exp-title').val();
  var rescuetime = $('#edit-rescuetime-checkbox-btn').is(':checked');
  var notif_window = $('#edit-notif-window-checkbox-btn').is(':checked');
  var is_mturk_study = $('#edit-is-mturk-study-checkbox-btn').is(':checked');
  var calendar = $('#edit-calendar-checkbox-btn').is(':checked');
  var geofence = $('#edit-geofence-checkbox-btn').is(':checked');
  // var text = $('#edit-text-checkbox-btn').is(':checked');
  // var image = $('#edit-image-checkbox-btn').is(':checked');
  var dashboard = $('#edit-dashboard-checkbox-btn').is(':checked');
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
    'notif_window': notif_window,
    'is_mturk_study': is_mturk_study,
    'calendar': calendar,
    'geofence': geofence,
    'text': dashboard === true,
    'image': dashboard === true,
    'reminder': reminder,
    'actuators': actuators
  };

  $.post(url, data).done(function(resp) {
    show_success_msg(response_field, '<br/>Experiment successfully updated. Reloading experiment...');
    window.location.href = window.location.origin + window.location.pathname;
  }).fail(function(error) {
    show_error_msg(response_field, error);
  });

});

$('#delete-experiment-btn').click(function() {
  if (confirm("Are you sure you want to delete this experiment permanently?") === true) {
    var code = $('#code_from_hidden_element').val();
    window.location.href = '/delete/experiment/{0}'.format(code);
  }
});

/////////////////////////////
// upload images and texts
/////////////////////////////
$('#upload-btn').click(function(event) {
  var image,
    text,
    response_field,
    form_data;
  event.preventDefault();

  image = $('#uploaded-image').get(0).files[0];
  text = $('#uploaded-text').val();
  response_field = '#upload-status';

  if (!image && !text) {
    show_error_msg(response_field, 'You need to add either an image and/or a text.');
    return;
  }

  form_data = new FormData();

  if (image) {
    form_data.append('image', image);
    form_data.append('image_name', image.name);
  }

  if (text) {
    form_data.append('text', text);
  }

  var code = $('#code_from_hidden_element').val();
  form_data.append('code', code);

  console.log('text going:', text);

  $.ajax({
    url: '/upload/intervention',
    success: function(resp) {
      show_success_msg(response_field, 'Successfully uploaded: ' + resp);
    },
    error: function(e) {
      show_error_msg(response_field, 'Upload error. Pls contact researcher. ' + e.statusText);
    },
    complete: function(e) {
      setTimeout(function() {
        show_plain_msg(response_field, '');
        $('#upload-image-modal').modal('hide');
        $('#uploaded-image').val('');
        $('#uploaded-text').val('');
        window.location.href = window.location.href;
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

/////////////////////////////
// create intervention table
/////////////////////////////
update_intv_table();

function update_intv_table() {
  create_new_intv_table();
  add_intv_row();
}

function create_new_intv_table() {

  var view,
    no_of_condition,
    other_headers,
    group_rows,
    row;

  no_of_condition = parseInt($('#no-of-condition').val());
  other_headers = 4;

  group_rows = '';
  for (var i = 0; i < no_of_condition; i++) {
    group_rows += '<th class="col-md-1"> Group{0} </th>'.format(i + 1);
  }

  view = '<table id="intvn-table-id"' +
    ' class="table table-striped table-bordered table-hover"><tr>' +
    group_rows +
    '<th class=col-md-1> Start </th>' +
    '<th class="col-md-1"> Every </th>' +
    '<th class="col-md-1"> Alarm Time </th>' +
    '<th class="col-md-1"> Repeat </th>' +
    '</tr><tbody></tbody></table>';

  $('#intv-table-view').html(view);
}

function to_date_fmt(date) {
  var mm = date.getMonth() + 1; // getMonth() is zero-based
  var dd = date.getDate();
  return [
    date.getFullYear(),
    (mm > 9 ? '' : '0') + mm,
    (dd > 9 ? '' : '0') + dd
  ].join('-');
}

function add_intv_row() {
  var no_of_condition,
    group_rows,
    new_row,
    intv_options,
    code,
    url,
    treat_id;

  no_of_condition = parseInt($('#no-of-condition').val());
  group_rows = '';

  code = $('#code_from_hidden_element').val();
  url = '/fetch/uploaded/features/' + code;

  $.get(url).done(function(all_features_str) {
    for (var j = 1; j <= no_of_condition; j++) {
      treat_id = 'treat-{0}'.format(j);
      intv_options = create_intv_options(all_features_str, treat_id);
      group_rows += '<td>{0}</td>'.format(intv_options);
    }

    var today = to_date_fmt(new Date());
    var date_input = '<input class="form-control" id="intv-start-date" data-provide="datepicker"' +
    'data-date-start-date="0d"' +
    'data-date-format="yyyy-mm-dd"' +
    'data-date-today-highlight=true' +
    'placeholder="select start date" value="{0}">'.format(today);

    new_row = '<tr class="del-row">' + group_rows + '<td> {0} </td>'.format(date_input) + '<td> {0} </td>'.format(create_every_options()) + '<td> <input type="time" class="form-control" id="intv-time" value="00:00:00.000"/> </td>' + '<td> <input type="number" id="intv-repeat" class="form-control" style="width: 80px" min=1 value=1 /> </td>' + '</tr>';

    $('#intvn-table-id').append(new_row);

  });
}

function create_intv_options(all_features_str, treat_id) {

  var i,
    delim,
    uploads,
    uploaded_options,
    rt_options,
    rt_specific,
    blank_options,
    calendar_options,
    show_dashboard,
    all_features,
    show_rt;

  all_features = JSON.parse(all_features_str);
  console.log('all_features: ', all_features);
  uploads = all_features.image_text_uploads;

  show_rt = $('#edit-rescuetime-checkbox-btn').is(':checked');
  delim = '**&&&&**';

  uploaded_options = '';
  show_dashboard = $('#edit-dashboard-checkbox-btn').is(':checked');
  if (show_dashboard) {

    for (i = 0; i < uploads.length; i++) {
      var upl = uploads[i];

      if (upl.image_name && upl.text) {
        uploaded_options += '<option class="image_text" value="{1}{0}{3}">{1} / {3}</option>'.format(delim, upl.image_url, upl.image_name, upl.text);
      } else if (upl.image_name) {
        uploaded_options += '<option class="image_text" value="{0}">{1}</option>'.format(upl.image_url, upl.image_name);
      } else if (upl.text) {
        uploaded_options += '<option class="image_text" value="{0}">{0}</option>'.format(upl.text);
      }
    }
    uploaded_options = '<optgroup label="Text / Image Uploads">' + uploaded_options + '</optgroup>';

  }

  rt_options = '';
  if (show_rt) {
    rt_options = '<option class="rescuetime"> focus & distracting time </option>' +
      '<option> only focus time </option>' +
      '<option> only distracting time </option';
    rt_options = '<optgroup label="RescueTime General">' + rt_options + '</optgroup>';

  }

  rt_specific = '';
  if (show_rt) {
    rt_specific = '<option class="rescuetime"> software development </option>' +
      '<option> social networking </option>' +
      '<option> productivity pulse </option>';
    rt_specific = '<optgroup label="RescueTime Specific">' + rt_specific + '</optgroup>';
  }

  show_calendar = $('#edit-calendar-checkbox-btn').is(':checked');
  calendar_options = '';
  if (show_calendar) {
    if (len(all_features.last_calendar_config) > 0) {
      var cc = all_features.last_calendar_config;
      var option = 'Count Limit: {0} event(s) / Time Limit: {1} hour(s)'.format(cc.event_num_limit, cc.event_time_limit);
      calendar_options = '<option class="calendar">{0}</option>'.format(option);
      calendar_options = '<optgroup label="Calendar Busy Limit">{0}</optgroup>'.format(calendar_options);
    }
  }

  var vibration_options = '';
  var show_vibration = $('#edit-actuators-checkbox-btn').is(':checked');
  if (show_vibration) {
    if (len(all_features.last_vibration_config) > 0) {
      var vv = all_features.last_vibration_config;
      var vv_option = 'Monitor: {0} / Limit: {1} secs ({2}x) / vibration: ({3}) / show stats: ({4})'.format(vv.app_id, vv.time_limit, vv.open_limit, vv.vibration_strength, vv.show_stats);
      vibration_options = '<option class="vibration">{0}</option>'.format(vv_option);
      vibration_options = '<optgroup label="Phone Vibration">{0}</optgroup>'.format(vibration_options);
    }

  }

  blank_options = '<optgroup label="No Intervention">' +
    '<option class="baseline"> ------ </option' +
    '</optgroup>';

  var options = '<select id="{0}" class="form-control">'.format(treat_id) +
    uploaded_options +
    rt_options +
    rt_specific +
    calendar_options +
    vibration_options +
    blank_options +
    ' </select>';

  return options;
}

function create_every_options() {
  var options = '<select id="intv-every" class="form-control">' +
    ' <option>Daily</option> ' +
    ' <option>Weekly</option> ' +
    ' </select>';
  return options;
}

$('#reset-table-btn').click(function() {
  $('#intv-table-view').html('');
  update_intv_table();
});

$('#save-group-btn').click(function() {

  var experiment_code = $('#code_from_hidden_element').val();
  var no_of_condition = parseInt($('#no-of-condition').val());
  var ps_per_condition = $('#ps-per-condition').val();

  var response_field = '#group-status';
  var url = '/update/group';
  var data = {
    'code': experiment_code,
    'no_of_condition': no_of_condition,
    'ps_per_condition': ps_per_condition
  };

  $.post(url, data).done(function(resp) {
    show_success_msg(response_field, 'Group info successfully updated. Refreshing...<br/>');
    setTimeout(function() {
      window.location.href = window.location.origin + window.location.pathname;
    }, 1000);
  }).fail(function(error) {
    show_error_msg(response_field, 'Error saving: ' + error.statusText);
  });

});

////////////////////
////////////////////
////////////////////
////////////////////
////////////////////
////////////////////

$('#save-table-btn').click(function() {
  var intv_notif = $('#intv-notif').find(":selected").val();
  var intv_every = $('#intv-every').val();
  var intv_repeat = $('#intv-repeat').val();
  var intv_time = $('#intv-time').val();
  var experiment_code = $('#code_from_hidden_element').val();

  var factor = intv_every === 'Daily' ? 1 : 7;
  var no_of_days = intv_repeat * factor;

  var intv_start_date = $('#intv-start-date').val();
  var intv_start_datetime = '{0}T00:00:00-05:00'.format(intv_start_date);
  intv_start_datetime = new Date(intv_start_datetime);

  var intv_end_datetime = '{0}T00:00:00-05:00'.format(intv_start_date);
  intv_end_datetime = new Date(intv_end_datetime);
  intv_end_datetime.setDate(intv_end_datetime.getDate() + no_of_days);
  intv_end_datetime = intv_end_datetime;

  var url = '/add/intervention';
  var data = {
    'condition': "0",
    'treatment': "",
    'intv_type': "calendar",
    'intv_notif': intv_notif,
    'code': experiment_code,
    'start': intv_start_datetime.toJSON(), // UTC
    'end': intv_end_datetime.toJSON(), // UTC
    'every': intv_every,
    'when': intv_time,
    'repeat': intv_repeat
  };

  var response_field = '#intv-table-status';
  $.post(url, data).done(function(resp) {
    show_success_msg(response_field, 'Intervention successfully saved.<br/>');
    console.log('success intv resp: ', resp);
    window.location.href = window.location.origin + window.location.pathname;
  }).fail(function(error) {
    show_error_msg(response_field, 'Error saving intervention: ' + error.statusText);
    console.log('intv save error:', error);
  });
});


////////////////////
////////////////////
////////////////////
////////////////////
////////////////////
////////////////////
////////////////////
////////////////////
////////////////////


$('#save-table-btnx').click(function() {

  var response_field = '#intv-table-status';
  var no_of_condition = parseInt($('#no-of-condition').val());
  var treatments = [];
  var treat_delim = '**&&&&**';
  var intv_type = 'text_image';

  for (var k = 1; k <= no_of_condition; k++) {
    var btn_id = '#treat-{0}'.format(k);
    console.log('class: ', $(btn_id).attr('class'));
    var treat = $(btn_id).val();
    console.log('treat: ', treat);
    if (treat)
      treatments.push(treat);
  }
  console.log('all_treaments: ', treatments);
  if (treatments.length === 0) {
    show_error_msg(response_field, 'Error: You need to upload images and/or texts before you apply any intervention.<br/>');
    return;
  }

  var delim = '%%&&';
  var all_treat_str = treatments.join(delim);

  if (all_treat_str.indexOf('event') > -1) {
    intv_type = 'calendar';
  } else if (all_treat_str.indexOf('Monitor') > -1) {
    intv_type = 'actuators';
  } else if (all_treat_str.indexOf('focus') > -1 || all_treat_str.indexOf('distracting') > -1) {
    intv_type = 'rescuetime';
  }

  var intv_time = $('#intv-time').val();
  intv_time = intv_time.indexOf('.') > -1 ? intv_time : '{0}:00'.format(intv_time);
  console.log('intv_time: ', intv_time);


  // use this to also save reminder time
  post_data('/mobile/add/daily-reminder-config',
    {
      'code': $('#code_from_hidden_element').val(),
      'reminder_time': intv_time
    },
    '#summary_entry');


  ////////////////////////////////////////////////
  // all experiments start and end at midnight
  // use NYC timezone
  ////////////////////////////////////////////////
  var intv_start_date = $('#intv-start-date').val();
  var intv_start_datetime = '{0}T00:00:00-05:00'.format(intv_start_date);
  intv_start_datetime = new Date(intv_start_datetime);

  var intv_every = $('#intv-every').val();
  var intv_repeat = $('#intv-repeat').val();
  intv_repeat = parseInt(intv_repeat);

  var factor = intv_every === 'Daily' ? 1 : 7;
  var no_of_days = intv_repeat * factor;

  var intv_end_datetime = '{0}T00:00:00-05:00'.format(intv_start_date);
  intv_end_datetime = new Date(intv_end_datetime);
  intv_end_datetime.setDate(intv_end_datetime.getDate() + no_of_days);
  intv_end_datetime = intv_end_datetime;

  var experiment_code = $('#code_from_hidden_element').val();
  if (experiment_code === '') {
    show_error_msg(response_field, 'Error: this experiment does not exist / has invalid code. You need to create a new one.<br/>');
    return;
  }

  var url = '/add/intervention';
  var data = {
    'code': experiment_code,
    'condition': no_of_condition,
    'treatment': all_treat_str,
    'start': intv_start_datetime.toJSON(), // UTC
    'end': intv_end_datetime.toJSON(), // UTC
    'every': intv_every,
    'when': intv_time,
    'intv_type': intv_type,
    'repeat': intv_repeat
  };

  $.post(url, data).done(function(resp) {
    show_success_msg(response_field, 'Intervention successfully saved.<br/>');
    console.log('success intv resp: ', resp);
    window.location.href = window.location.origin + window.location.pathname;
  }).fail(function(error) {
    show_error_msg(response_field, 'Error saving intervention: ' + error.statusText);
    console.log('intv save error:', error);
  });

});

$('#remove-row-btn').click(function() {
  $('#intvn-table-id tr:last').remove();
});

/////////////////////////////
/// delete archived intv ////
/////////////////////////////
$('#delete-intv-btn').click(function() {
  if (confirm("Are you sure you want to delete permanently?") === true) {
    var resp = $('#delete-intv-btn').val();
    console.log('confirm resp: ', resp);
  // window.location.href = '/delete/experiment/{0}'.format(code);
  }
});

////////////////////////////////
///// calendar functions ///////
////////////////////////////////

// reset all previous entries
$('#reset-btn').click(function() {

  var r = confirm("Are you sure about resetting calendar? Everything will be wiped out.");
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
  var r = confirm("Are you sure about changing calendar? Current data will be discarded.");
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
  var r = confirm("Are you sure you want to completely remove calendar?");
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

    if (typeof (resp) === 'string') {
      show_success_msg(response_field, resp);
      return;
    }

    var result = JSON.parse(resp);
    result = typeof (result) !== 'object' ? JSON.parse(result) : result;

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

    if (typeof (resp) === 'string') {
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

    if (typeof (resp) === 'string') {
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
    'gender': gender
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
  $me.delay(2000 + 800 * index).fadeTo(200, 0).slideUp(200, function() {
    $me.alert('close');
  });
});
