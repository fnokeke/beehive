// '<td><button id={1} class="btn btn-link">{0}</button></td>'.format(exp.title, exp.code)

$('#download-gcal-btn').click(function() {
    alert("Hello test");
    window.location.href = '/gcal/download/{0}/{1}'.format("test", "test2");
});
