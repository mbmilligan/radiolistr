$(document).ready(function() {
	$('#playlist-table').bootstrapTable()
	$('#playlist-table tr.no-records-found td').text('No tracks loaded yet...')

	$('#fileUpload').ajaxForm({
		dataType: 'json',
		success: function(r) {
			$('#resTxt').text(JSON.stringify(r,null,2))
			$('table#playlist-table').bootstrapTable('load', r);
			$('#sendFile').removeClass('btn-primary').addClass('btn-success');
			$('#getLabels').removeClass('btn-default btn-success').addClass('btn-primary');
			$('#getSMText').removeClass('btn-primary').addClass('btn-default');
			$('#getFile').removeClass('btn-primary').addClass('btn-default');
		}
	});

	$('#getLabels').click(function () {
		var bt = $('#playlist-table');
		var data = bt.bootstrapTable('getData');
		var doLoop = function (i, list, defer) {
			if (!defer) { defer = $.Deferred(); }
			while (i in list && !(list[i].artist && list[i].album)) {
				i += 1;
			}
			if (i in list) {
				$.getJSON(document.location.pathname + 'getinfo', { listdata: JSON.stringify([list[i]]) })
					.done(function(res) {
						if('label' in res[0]) {
							$.extend(list[i], res[0]);
							bt.bootstrapTable('load', list);
						};
					})
					.always(function(){ doLoop(i+1, list, defer) });
			}
			else { defer.resolve(); }
			return defer;
		};
		$('#getLabels').removeClass('btn-default btn-primary btn-success').addClass('btn-danger');
		doLoop(0, data).done(function() {
			$('#getLabels').removeClass('btn-danger').addClass('btn-success');
			$('#getSMText').removeClass('btn-default').addClass('btn-primary');
			$('#getFile').removeClass('btn-default').addClass('btn-primary');
		});
	});

	$('#getSMText').click(function () {
		d = $('#playlist-table').bootstrapTable('getData');
		alert(d.map(function(i) { return i.artist + ' - "' + i.title + '" - ' + i.album }).join('\n'));
	});
	
	$('#getFile').click(function () {
		var q = { date: $('#showdate').val(),
				  listdata: JSON.stringify( $('#playlist-table').bootstrapTable('getData') )
			  };
		$('#getFile-listdata').val(q.listdata);
		$('#getFile-date').val(q.date);
		return $('#gFForm form').submit();
		$('#gFForm form').ajaxSubmit({
			iframe: true,
			dataType: null,
			success: null
		});
	});
});
