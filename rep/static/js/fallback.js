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

  if (!window.bootstrap) {
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
    document.write('<script src="{0}">\x3C/script>'.format(filepath));
  }

  function insert_css(filepath) {
    document.write('<link rel="stylesheet" href="{0}"/>'.format(filepath));
    // document.write('<script type="text/css" src="{0}">\x3C/script>'.format(filepath));
  }


})(window, document);
