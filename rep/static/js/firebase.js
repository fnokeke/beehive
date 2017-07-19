
$('#firebase-sync-btn').click(function(event) {
  event.preventDefault();

  var token = $('#firebase-sync-token').val();
  var response_field = '#firebase-sync-response';


  if (token === '') {
    show_error_msg(response_field, 'Please submit a valid token.');
    return;
  }
  console.log('token: ', token);

  var url = '/firebase/sync';
  var data = {
    'firebase_sync_token': token
  };

  $.post(url, data).done(function(resp) {
    var json_resp = JSON.parse(resp);
    console.log('json_resp: ');
    if (json_resp.failure === 1) {
      show_error_msg(response_field, "Syncing Error: " + json_resp.results[0].error);
    } else {
      show_success_msg(response_field, "Successfully Synced: " + resp);
    }

  }).fail(function(error) {
    var msg = 'Error submitting token. Please contact researcher. (Error: {0} / {1}).'.format(error.status, error.statusText);
    show_error_msg(response_field, msg);
  });

});
