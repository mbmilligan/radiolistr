roaelistr : Make playlists for ROAE on KFAI
====================

Dependencies
------------

flask, flask-bootstrap, Flask-WTF*

* consider dropping WTF, doesn't add much to what we're doing here

requests

lxml

pandas

In principle, all of these can be installed via pip.

In practice, it is likely much easier to use the system packaged lxml and pandas,
rather than bother with compliling those libraries their dependencies.

Therefore, in this environment, what we have done is:

	apt-get install python-lxml python-pandas
	virtualenv --system-site-packages python
	(python) pip install flask flask-bootstrap Flask-WTF requests

In addition, note that we are using a number of front-end components that are pulled from CDNs:

<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.4/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.4.0/js/bootstrap-datepicker.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.8.1/bootstrap-table.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.form/3.51/jquery.form.min.js"></script>
