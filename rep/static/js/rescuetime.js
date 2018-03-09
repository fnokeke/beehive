
$('#select-days').change(function() {
    var days = $('#select-days').val()
    window.location.href = '/rescuetime/stats?days={0}'.format(days );
});