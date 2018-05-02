$(document).ready(function() {
  var page_length = 10;

  $('#experiment-participants-table').DataTable({
    "pageLength": page_length
  });

  $('#experiment-app-analytics-table').DataTable({
    "pageLength": page_length
  });

  $('#experiment-protocols-table').DataTable({
    "pageLength": page_length
  });

   $('#experiment-app-usage-table').DataTable({
    "pageLength": page_length
  });


  $('#experiment-screen-events-table').DataTable({
    "pageLength": page_length
  });


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
    responsive: true,
    "serverSide": true,
    "processing": true,
    ajax: {
      url: '/server-fb-stats',
      method: 'post',
      data: function(params) {
        console.log('params sent:', params);
        return {
          "params": JSON.stringify(params)
        };
      },
    }
  });
});
