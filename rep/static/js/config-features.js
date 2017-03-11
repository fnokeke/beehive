
(function(window, document) {

  var span = ' <span onclick=';
  var x_glyph = ' class="glyphicon glyphicon-remove text-danger"></span>';
  var entry;

  $('#calendar_config').click(function() {
    $('#calendar_config').hide();
    entry = '<div id="calendar_entry"> <a onclick="edit_calendar()">Edit Calendar Settings</a>' +
      '<span onclick="x_calendar() "' + x_glyph + '</div>';
    $(entry).appendTo('#selected_configs');
  });

  $('#general_notif_config').click(function() {
    $('#general_notif_config').hide();
    entry = '<div id="status_notif_entry"> <a onclick="edit_general_notif()">General Notification Settings</a>' +
      '<span onclick="x_general_notif() "' + x_glyph + '</div>';
    $(entry).appendTo('#selected_configs');
  });

  $('#rescuetime_config').click(function() {
    $('#rescuetime_config').hide();
    entry = '<div id="rescuetime_entry"> <a onclick="edit_rescuetime()">Configure RescueTime</a>' +
      '<span onclick="x_rescuetime() "' + x_glyph + '</div>';
    $(entry).appendTo('#selected_configs');
  });

  $('#vibration_config').click(function() {
    $('#vibration_config').hide();
    entry = '<div id="vibration_entry"> <a onclick="edit_vibration()">Set Vibration Strength</a>' +
      '<span onclick="x_vibration() "' + x_glyph + '</div>';
    $(entry).appendTo('#selected_configs');
  });

  $('#screen_unlock_config').click(function() {
    $('#screen_unlock_config').hide();
    entry = '<div id="screen_unlock_entry"> <a onclick="edit_screen_unlock()">Screen Unlock Settings</a>' +
      '<span onclick="x_screen_unlock() "' + x_glyph + '</div>';
    $(entry).appendTo('#selected_configs');
  });

  ///////////////////////
  // modal save buttons
  ///////////////////////

  $("#save-vibration-modal").click(function() {
    var app_id;
    var app_time_limit;
    var app_opens_limit;
    var show_stats;
    var strength;
    var summary;

    app_id = $('#vibration-app-id').val();
    app_time_limit = $('#vibration-time-limit').val();
    app_opens_limit = $('#vibration-opens-limit').val();
    show_stats = $('#show-vibration-stats').is(':checked');
    strength = $('#vibration-strength-response input:radio:checked').val();

    summary = "app_id: {0} / time limit: {1} / open limit: {2} / show stats: {3} / vibration strength: {4}".format(
      app_id, app_time_limit, app_opens_limit, show_stats, strength);

    $('#summary_entry').empty();
    entry = '<p>Vibration settings: ' + summary + '</p>';
    $(entry).appendTo('#summary_entry');

    post_data('/mobile/add/vibration-config',
      {
        'code': $('#code_from_hidden_element').val(),
        'app_id': app_id,
        'time_limit': app_time_limit,
        'open_limit': app_opens_limit,
        'show_stats': show_stats,
        'vibration_strength': strength
      },
      '#summary_entry');

  });

  $("#save-rescuetime-modal").click(function() {
    var productive_time;
    var distracted_time;
    var productive_msg;
    var distracted_msg;
    var persistence;
    var summary;

    productive_time = $('#rescuetime-time-productive').val();
    distracted_time = $('#rescuetime-time-distracted').val();
    productive_msg = $('#productive-notif-msg').val();
    distracted_msg = $('#distracted-notif-msg').val();
    persistence = $('#show-persistent-rescuetime-stats').is(':checked');

    summary = "productive: {0} ({1}) / distracted: {2} ({3}) / persistence: {4}".format(
      productive_time, productive_msg, distracted_time, distracted_msg, persistence);

    $('#summary_entry').empty();
    entry = '<p>Rescuetime settings: ' + summary + '</p>';
    $(entry).appendTo('#summary_entry');

    post_data('/mobile/add/rescuetime-config',
      {
        'code': $('#code_from_hidden_element').val(),
        'productive_duration': productive_time,
        'distracted_duration': distracted_time,
        'productive_msg': productive_msg,
        'distracted_msg': distracted_msg,
        'show_stats': persistence
      },
      '#summary_entry');
  });

  $("#save-general-notif-modal").click(function() {
    var title;
    var content;
    var app_to_launch;

    var msg;

    title = $('#notif-title').val();
    content = $('#notif-content').val();
    app_to_launch = $('#app-id-to-launch').val();

    console.log('title: ', title);
    console.log('content: ', content);
    console.log('app_to_launch: ', app_to_launch);

    if (app_to_launch === '') {
      app_to_launch = 'default';
    }

    msg = "title: {0} / content: {1} / app-to-launch: {2}".format(title, content, app_to_launch);
    $('#summary_entry').empty();
    var entry = '<p>General Status Notification: ' + msg + '</p>';
    $(entry).appendTo('#summary_entry');

    post_data('/mobile/add/general-notification-config',
      {
        'code': $('#code_from_hidden_element').val(),
        'title': title,
        'content': content,
        'app_id': app_to_launch
      },
      '#summary_entry');
  });

  $("#save-calendar-modal").click(function() {
    var max_events = '';
    var max_time = '';
    var settings = '';

    max_events = $('#calendar-max-events').val();
    max_time = $('#calendar-max-hours').val();

    if (max_events === '') {
      settings += 'Max events: ' + max_events + " / ";
    }

    if (max_time === '') {
      settings += 'Max hours: ' + max_time;
    }

    if (settings === '') {
      settings = 'No limits set.';
    }

    $('#summary_entry').empty();
    var entry = '<p>Calendar setting: ' + settings + '</p>';
    $(entry).appendTo('#summary_entry');

    post_data('/mobile/add/calendar-config',
      {
        'code': $('#code_from_hidden_element').val(),
        'event_time_limit': max_time,
        'event_num_limit': max_events
      },
      '#summary_entry');
  });

  $("#save-screen-unlock-modal").click(function() {
    var summary = '<p>screen unlock save tapped.</p>';
    console.log(summary);
    $(summary).appendTo('#summary_entry');

    post_data('/mobile/add/screen-unlock-config',
      {
        'code': $('#code_from_hidden_element').val(),
        'time_limit': $('#time-limit').val(),
        'unlocked_limit': $('#unlocked-limit').val(),
        'vibration_strength': $('#unlock-vibration-strength input:radio:checked').val(),
        'show_stats': $('#show-unlock-stats').is(':checked'),
        'enable_user_pref': $('#user-monitor-pref').is(':checked'),
        'start_time': $('#monitor-unlock-start').val(),
        'end_time': $('#monitor-unlock-end').val()
      },
      '#summary_entry');
  });

  $('#user-monitor-pref').change(function() {
    var is_checked = $('#user-monitor-pref').is(':checked');
    if (is_checked) {
      $('#custom-monitoring-pref :input').prop("disabled", true);
    } else {
      $('#custom-monitoring-pref :input').prop("disabled", false);
    }
  });

})(window, document);

/////////////////////////////////
// edit entries
/////////////////////////////////
function edit_calendar() {
  $('#calendar-modal').modal('show');
}

function edit_general_notif() {
  $('#general-notif-modal').modal('show');
}

function edit_rescuetime() {
  $('#rescuetime-modal').modal('show');
}

function edit_vibration() {
  $('#vibration-modal').modal('show');
}

function edit_screen_unlock() {
  $('#screen-unlock-modal').modal('show');
}

/////////////////////////////////
// remove config
/////////////////////////////////

function x_calendar() {
  $('#calendar_entry').remove();
  $('#calendar_config').show();
}

function x_general_notif() {
  $('#general_notif_entry').remove();
  $('#general_notif_config').show();
}

function x_rescuetime() {
  $('#rescuetime_entry').remove();
  $('#rescuetime_config').show();
}

function x_text_image() {
  $('#text_image_entry').remove();
  $('#text_image_config').show();
}

function x_vibration() {
  $('#vibration_entry').remove();
  $('#vibration_config').show();
}

function x_screen_unlock() {
  $('#screen_unlock_entry').remove();
  $('#screen_unlock_config').show();
}

function post_data(url, data, response_field) {
  $.post(url, data).done(function(json_string) {
    var results = JSON.parse(json_string);
    show_success_msg(response_field, results.response);
    window.location.href = window.location.origin + window.location.pathname;
  }).fail(function(error) {
    var msg = 'Error. Pls contact researcher (Error: {0} / {1}).'.format(error.status, error.statusText);
    show_error_msg(response_field, msg);
  });
}
