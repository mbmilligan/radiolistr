from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import TextField, TextAreaField, HiddenField, ValidationError, RadioField,\
BooleanField, SubmitField, IntegerField, FormField, validators

import metallum
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'roae'
Bootstrap(app)

class MainForm(Form):
	listdata = TextAreaField('Playlist Data')
	submitted = SubmitField('Process Data')

@app.route('/')
# Change to serve just static homepage with HTML5 controls
def starter():
	return render_template('input.html', form=MainForm())

@app.route('/getinfo', methods=['GET','POST'])
# AJAX route accepts playlist data, does lookups and streams back label data
def gettrackinfo():
	tracks = json.loads(request.form['listdata'])
	out = []
	for l in tracks:
		try:
			out.append(metallum.getalbumdata(l['artist'], l['album']))
		except:
			out.append('ERROR')
	return json.dumps(out)

@app.route('/readtable', methods=['POST'])
# route for uploading a csv/xls file (whatever Pandas can handle),
# returns JSON version of table formatted for gettrackinfo
def readtabfile():
	return ""

@app.route('/getxls', methods=['GET','POST'])
# accept gettrackinfo data (possibly edited client-side)
# return Pandas-generated xls file for upload as playlist
def getxls():
	return ""

if __name__ == '__main__':
    app.run(debug=True)
