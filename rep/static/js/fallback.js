(function(window, document) {

  var filepath;

  if (!window.jQuery) {
    filepath = '/static/lib/js/jquery.min.js';
    insert_script(filepath);
  }

  if (!window.vis) {
    filepath = '/static/lib/js/vis.min.js';
    insert_script(filepath);
  }

  var bootstrap_enabled = (typeof $().modal == 'function');

  // Load fallbacks only if Bootstrap was not loaded from CDN
  if (!bootstrap_enabled) {
    filepath = '/static/lib/js/bootstrap.js';
    insert_script(filepath);

    filepath = '/static/lib/css/bootstrap.min.css';
    insert_css(filepath);

    filepath = '/static/lib/css/vis.min.css';
    insert_css(filepath);

    filepath = '/static/lib/css/bootstrap-theme.min.css';
    insert_css(filepath);

    filepath = '/static/lib/css/bootstrap-datepicker.css';
    insert_css(filepath);
  }

  if (!window.datepicker) {
    filepath = '/static/lib/js/bootstrap-datepicker.min.js';
    insert_script(filepath);
  }

  if (!window.confirmation) {
    filepath = '/static/lib/js/bootstrap-confirmation.min.js';
    insert_script(filepath);
  }

  function insert_script2(filepath) {
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.src = filepath;
    head.appendChild(script);
  }

  function insert_script(filepath) {
    var js_path = '<script src="' + filepath + '"><\/script>';
    document.write(js_path);

  }

  function insert_css(filepath) {
    var css_path = '<link rel stylesheet="' + filepath + '"/>';
    document.write(css_path);
  }

})(window, document);
