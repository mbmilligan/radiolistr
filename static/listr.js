var jresp = ''
$(document).ready(function() {
	$('#playlist-table').bootstrapTable()
	$('#playlist-table tr.no-records-found td').text('No tracks loaded yet...')
	$('#fileUpload').ajaxForm({
		dataType: 'json',
		success: function(r) {
			$('#resTxt').text(JSON.stringify(r,null,2))
			$('table#playlist-table').bootstrapTable('load', r);
			jresp = r
		}
	});
});
