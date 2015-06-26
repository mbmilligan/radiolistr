from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import TextField, TextAreaField, DateField, HiddenField, ValidationError, SubmitField, IntegerField, FormField, validators
from wtforms.widgets.html5 import DateInput

import metallum
import roaetables
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'roae'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024
Bootstrap(app)

@app.route('/')
# Change to serve just static homepage with HTML5 controls
def starter():
	return render_template('index.html')

@app.route('/getinfo', methods=['GET','POST'])
# AJAX route accepts playlist data, does lookups and streams back label data
def gettrackinfo():
	tracks = json.loads(request.args['listdata'])
	out = []
	for l in tracks:
		try:
			if l['artist'] and l['album']:
				out.append(metallum.getalbumdata(l['artist'], l['album']))
			else:
				out.append(dict(result='ERROR'))
		except:
			out.append(dict(result='ERROR'))
	return json.dumps(out, ensure_ascii=False)

@app.route('/readtable', methods=['POST'])
# route for uploading a csv/xls file (whatever Pandas can handle),
# returns JSON version of table formatted for gettrackinfo
def readtabfile():
	f = request.files['showfile']
	return roaetables.table2json(f, f.filename)

@app.route('/getxls', methods=['GET','POST'])
# accept gettrackinfo data (possibly edited client-side)
# return Pandas-generated xls file for upload as playlist
def getxls():
	return ""

@app.route('/e')
def echor():
	return "Got: " + request.args.get('e','')

if __name__ == '__main__':
    app.run(debug=True)
