import pandas as pd
import re
from tempfile import NamedTemporaryFile
from os import remove

def read_xls_or_csv(f, name):
	if name.lower().endswith('.xls'):
		d = pd.read_excel(f, sheetname=0)
	elif name.lower().endswith('.csv'):
		d = pd.read_csv(f)
	else:
		raise ValueError('Unrecognized file type: %s' % (name,))
	return d.dropna(how='all')

def find_columns(df):
	colptrns = [
		[ r'(?:artist|band)\b', 'artist' ],
		[ r'(?:title|track)\b(?!.*#|number)', 'title' ],
		[ r'(?:album|release)\b', 'album' ],
		[ r'(?:label)\b', 'label' ],
		[ r'(?:time|duration)\b', 'time' ]
	]
	colptrns = [ [ re.compile(p[0], re.IGNORECASE), p[1] ] for p in colptrns ]
	tgt = dict()
	for pat, col in colptrns:
		for cname in df.columns:
			if pat.match(cname):
				tgt[col] = df[cname]
	return pd.DataFrame(tgt)

def make_xls(df, path):
	ldf = df.copy()
	cols = ['artist','title','album','label','time']
	for c in cols:
		if c not in ldf:
			ldf[c] = ''
	outdf = ldf[cols]
	ew = pd.ExcelWriter(path, engine='xlwt')
	outdf.to_excel(ew, columns=cols, sheet_name="Tracks",
		header=map(lambda s: s.title(), outdf.columns),
		index=False, encoding='utf8', float_format='%.2f')
	for c, w in [(0, 20), (1, 50), (2, 40), (3, 20), (4, 10)]:
		ew.sheets["Tracks"].col(c).width = 260*w
	ew.save()
	ew.close()
	return path

def json2df(data):
	return pd.read_json(data, orient='records')

def df2json(df):
	return df.to_json(orient='records', force_ascii=False)

def table2json(f, path):
	return df2json(find_columns(read_xls_or_csv(f, path)))

def fixtimefn(time):
	try:
		m, s = time.split(':')
		retv = float(m) + float(s)/100.0
	except:
		retv = time
	try:
		if int(retv) == retv:
			retv += 0.01
	except:
		pass
	return retv

def fixtime(df, col):
	df[col] = df[col].map(fixtimefn, na_action='ignore')

def json2xls(data, path):
	df = json2df(data)
	fixtime(df, 'time')
	make_xls(df, path)

