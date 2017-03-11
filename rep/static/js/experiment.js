var experiment = (function() {

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


  $('#update-experiment-btn').click(function() {
    var code = $('#code_from_hidden_element').val();
    var title = $('#edit-exp-title').val();
    var start = $('#edit-start-date').val();
    var end = $('#edit-end-date').val();
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
      'start': start,
      'end': end,
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


})();
