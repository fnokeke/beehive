(function(window, document) {

  $('#step1-basic').click(function() {
    show_slide(1);
  });

  $('#step2-data').click(function() {
    show_slide(2);
  });

  $('#step3-protocols').click(function() {
    show_slide(3);
  });

  $('#step4-approve').click(function() {
    show_slide(4);
  });

  function show_slide(num) {
    $('#slide1').hide();
    $('#slide2').hide();
    $('#slide3').hide();
    $('#slide4').hide();
    $('#slide' + num).show();
  }

})(window, document);
