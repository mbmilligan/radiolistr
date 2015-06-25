roaelistr : Make playlists for ROAE on KFAI
====================

Dependencies
------------

flask, flask-bootstrap, Flask-WTF, Flask-Uploads*

* consider dropping WTF, Uploads, they don't add much to what we're doing here

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
