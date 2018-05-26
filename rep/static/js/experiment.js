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

// Function that updates the experiment view
  function update_experiment_view() {
    var view,
      exp,
      row,
      response_field;
    response_field = '#experiment-view-status';

    var url = '/fetch/experiments';
    var url_v2 =  '/fetch/experiments/v2';
    $.get(url_v2, function(results) {
      var experiments = JSON.parse(results);
      var view = create_experiment_view(experiments);
      var view_v2 = create_experiment_view_v2(experiments);
      $('#experiment-list-view').html(view_v2);
    }).fail(function(error) {
      show_error_msg(response_field, 'Could not load experiment view.');
      console.warn(error);
    });
  }

// Function to populate the experiments table
  function create_experiment_view(experiments) {
    view = '<table id="exp-list-table" class="table table-striped table-bordered"><tr>' +
      '<th class="center-text"> Title </th>' +
      '<th class="center-text"> Code </th>'  +
      '<th class="center-text"> Start </th>'  +
      '<th class="center-text"> End </th>'  +
      '</tr><tbody>';

    // Add each experiment details to the table
    for (var i = experiments.length - 1; i >= 0; i--) {
      exp = experiments[i];

      row = '<tr>' +
        '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code) +
        '<td class="center-text">' + exp.code + '</td>' +
        '<td class="center-text">' + formatDate(exp.start) + '</td>' +
        '<td class="center-text">' + formatDate(exp.end) + '</td>' +
        '</tr>';

      view += row;
    }

    view += '</tbody></table>';
    return view;
  }


  // Function to populate the experiments table v2
  function create_experiment_view_v2(experiments) {
    view = '<table id="exp-list-table" class="table table-striped table-bordered"><tr>' +
      '<th class="center-text"> Title </th>' +
      '<th class="center-text"> Code </th>'  +
      '<th class="center-text"> Start Date</th>'  +
      '<th class="center-text"> End Date</th>'  +
      '</tr><tbody>';

    // Add each experiment details to the table
    for (var i = experiments.length - 1; i >= 0; i--) {
      exp = experiments[i];

      row = '<tr>' +
        // '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code) +
        // '<td class="">' + exp.title + '</td>' +
        '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code) +
        '<td class="center-text">' + exp.code + '</td>' +
        '<td class="center-text">' + formatDate(exp.start_date) + '</td>' +
        '<td class="center-text">' + formatDate(exp.end_date) + '</td>' +
        '</tr>';

      view += row;
    }

    view += '</tbody></table>';
    return view;
  }

  /////////////////////////////
  // Format Date
  /////////////////////////////
  function formatDate(rawDate){
    var date = new Date(rawDate);
    date = date.toString().slice(0,15);
    return date;
  }

  /////////////////////////////
  // OnClick handler for experiment click
  /////////////////////////////
  /*
  $(document).on('click', '#exp-list-table .btn-link', function() {
    var code = this.id;
    window.location.href = '/edit-experiment/{0}'.format(code);
  });
*/

  $(document).on('click', '#exp-list-table .btn-link', function() {
    var code = this.id;
    window.location.href = '/experiment/{0}'.format(code);
  });



  $('#update-experiment-btn').click(function() {
    var code = $('#code_from_hidden_element').val();
    var title = $('#edit-exp-title').val();
    var start = $('#edit-start-date').val();
    var end = $('#edit-end-date').val();
    var rescuetime = $('#edit-rescuetime-checkbox-btn').is(':checked');
    var is_notif_window_enabled = $('#edit-notif-window-checkbox-btn').is(':checked');
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
      'is_notif_window_enabled': is_notif_window_enabled,
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


