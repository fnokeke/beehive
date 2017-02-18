
(function(window, document) {

  var span = ' <span onclick=';
  var x_glyph = ' class="glyphicon glyphicon-remove text-danger"></span>';
  var entry;

  $('#reminder_config').click(function() {
    $('#reminder_config').hide();
    entry = '<div id="reminder_entry"> <a onclick="edit_reminder()">Edit Daily Reminder</a>' +
      '<span onclick="x_reminder() "' + x_glyph + '</div>';
    $(entry).appendTo('#selected_configs');
  });

  $('#calendar_config').click(function() {
    $('#calendar_config').hide();
    entry = '<div id="calendar_entry"> <a onclick="edit_calendar()">Edit Calendar Settings</a>' +
      '<span onclick="x_calendar() "' + x_glyph + '</div>';
    $(entry).appendTo('#selected_configs');
  });

  $('#status_notif_config').click(function() {
    $('#status_notif_config').hide();
    entry = '<div id="status_notif_entry"> <a onclick="edit_status_notif()">General Notification Settings</a>' +
      '<span onclick="x_status_notif() "' + x_glyph + '</div>';
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

  ///////////////////////
  // modal save buttons
  ///////////////////////
  $("#save-reminder-modal").click(function() {
    var user_pref;
    var result;

    result = $('#custom-time').val();
    user_pref = $('#user-pref-response input:radio:checked').val();
    if (user_pref === 'on') {
      result = 'user-pref';
    }

    console.log('result: ', result);

    $('#summary_entry').empty();
    var entry = '<p>Alarm Reminder: ' + result + '</p>';
    $(entry).appendTo('#summary_entry');
  });

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
  });

  $("#save-status-notif-modal").click(function() {
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
  });

  $("#save-calendar-modal").click(function() {
    var max_events = -1;
    var max_hours = -1;
    var settings = '';

    max_events = $('#calendar-max-events').val();
    max_hours = $('#calendar-max-hours').val();

    if (max_events > -1) {
      settings += 'Max events: ' + max_events + " ";
    }

    if (max_hours > -1) {
      settings += 'Max seconds: ' + max_hours;
    }

    if (settings === '') {
      settings = 'No limits set.';
    }

    $('#summary_entry').empty();
    var entry = '<p>Calendar setting: ' + settings + '</p>';
    $(entry).appendTo('#summary_entry');
  });

})(window, document);

/////////////////////////////////
// edit entries
/////////////////////////////////
function edit_reminder() {
  $('#reminder-modal').modal('show');
}

function edit_calendar() {
  $('#calendar-modal').modal('show');
}

function edit_status_notif() {
  $('#status-notif-modal').modal('show');
}

function edit_rescuetime() {
  $('#rescuetime-modal').modal('show');
}

function edit_vibration() {
  $('#vibration-modal').modal('show');
}

/////////////////////////////////
// remove config
/////////////////////////////////
function x_reminder() {
  $('#reminder_entry').remove();
  $('#reminder_config').show();
}

function x_calendar() {
  $('#calendar_entry').remove();
  $('#calendar_config').show();
}

function x_status_notif() {
  $('#status_notif_entry').remove();
  $('#status_notif_config').show();
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
