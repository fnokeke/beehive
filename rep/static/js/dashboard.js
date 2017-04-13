$(document).ready(function() {
  var page_length = 50;

  $('#enrolled-participants-table').DataTable({
    "pageLength": page_length
  });

  $('#notif-clicked-table').DataTable({
    "pageLength": page_length
  });

  $('#stats-table').DataTable({
    "pageLength": page_length,
    "bDeferRender": true,
  });

  $('#mturk-participants-table').DataTable({
    "pageLength": page_length,
    "bDeferRender": true,
  });

  $('#mturk-stats-table').DataTable({
    "pageLength": page_length,
    "bDeferRender": true,
    "bProcessing": true,
  });
});
