$(document).ready(function() {
	$('#playlist-table').bootstrapTable()
	$('#playlist-table tr.no-records-found td').text('No tracks loaded yet...')

	$('#fileUpload').ajaxForm({
		dataType: 'json',
		success: function(r) {
			$('#resTxt').text(JSON.stringify(r,null,2))
			$('table#playlist-table').bootstrapTable('load', r);
			$('#sendFile').removeClass('btn-primary').addClass('btn-success')
			$('#getLabels').removeClass('btn-default').addClass('btn-primary')
		}
	});

	$('#getLabels').click(function () {
		var bt = $('#playlist-table');
		var data = bt.bootstrapTable('getData');
		var doLoop = function (i, list, defer) {
			if (!defer) { defer = $.Deferred(); }
			while (i in list && !('artist' in list[0] && 'album' in list[0])) {
				i += 1;
			}
			if (i in list) {
				$.getJSON('/getinfo', { listdata: JSON.stringify([list[i]]) })
					.done(function(res) {
						if('label' in res[0]) {
							list[i].label = res[0].label;
							list[i].artist = res[0].artist;
							list[i].album = res[0].album;
							bt.bootstrapTable('load', list);
						};
					})
					.always(function(){ doLoop(i+1, list, defer) });
			}
			else { defer.resolve(); }
			return defer;
		};
		$('#getLabels').removeClass('btn-default').removeClass('btn-primary')
			.addClass('btn-danger');
		doLoop(0, data).done(function() {
			$('#getLabels').removeClass('btn-danger').addClass('btn-success');
			$('#getSMText').removeClass('btn-default').addClass('btn-primary');
			$('#getFile').removeClass('btn-default').addClass('btn-primary');
		});
	});
			
});
