// enable string formatting: '{0}{1}'.format(var1, var2)
String.prototype.format = function() {
  var args = arguments;
  return this.replace(/\{(\d+)\}/g, function(m, n) {
    return args[n];
  });
};

function show_success_msg(div, msg) {
  $(div).html(msg).css('color', 'green');
}

function show_plain_msg(div, msg) {
  $(div).html(msg).css('color', 'black');
}

function show_error_msg(div, msg) {
  $(div).html(msg).css('color', 'red');
}


function delete_intv(intv) {
  var prompt = "Are you sure you want to delete permanently?\nIntervention created at: {0}".format(intv.created_at);
  if (confirm(prompt) === false) {
    return;
  }

  var response_field = '#delete-intv-status';
  var url = '/delete/intervention';
  var data = {
    'created_at': intv.created_at
  };

  $.post(url, data).done(function(resp) {
    show_success_msg(response_field, resp);
    window.location.href = window.location.href;
  }).fail(function(error) {
    show_error_msg(response_field, error.statusText);
  });
}

function len(obj) {
  return Object.keys(obj).length;
}
