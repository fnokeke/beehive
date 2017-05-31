(function(window, document) {

  $('#step1').click(function() {
    show_slide(1);
  });

  $('#step2').click(function() {
    show_slide(2);
  });

  $('#step3').click(function() {
    show_slide(3);
  });

  $('#step4').click(function() {
    show_slide(4);
  });

  $('#step5').click(function() {
    show_slide(5);
  });

  function show_slide(num) {
    $('#slide1').hide();
    $('#slide2').hide();
    $('#slide3').hide();
    $('#slide4').hide();
    $('#slide5').hide();
    $('#slide' + num).show();
  }

})(window, document);
