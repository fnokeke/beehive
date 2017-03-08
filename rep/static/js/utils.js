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


function show_success_msg(div, msg) {
  $(div).html(msg).css('color', 'green');
}

function show_plain_msg(div, msg) {
  $(div).html(msg).css('color', 'black');
}

function show_error_msg(div, msg) {
  $(div).html(msg).css('color', 'red');
}

function len(obj) {
  return Object.keys(obj).length;
}
