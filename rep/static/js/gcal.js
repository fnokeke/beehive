// '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code)

$('#download-gcal-btn').click(function() {
    var start = $('#gcal-start-date').val();
    var end = $('#gcal-end-date').val();

    //alert("start:" + start + "  end:" + end)
    if (start=="" || end ==""){
        alert("Please enter start and end dates")
        return;
    }
    window.location.href = '/gcal/download/{0}/{1}'.format(start, end);
});
