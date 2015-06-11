from flask import Flask, request, render_template
import metallum

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def starter():
	if request.method == 'GET':
		return render_template('input.html')
	else:
		tracks = request.form['input']
		out = []
		for l in tracks.split('\n'):
			try:
				out.append(metallum.getlabel(l)['label'])
			except:
				out.append('NOT FOUND')
		return '<br />\n'.join(out)

if __name__ == '__main__':
    app.run()
