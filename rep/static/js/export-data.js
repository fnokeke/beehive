
(function(window, document) {

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

})(window, document);
