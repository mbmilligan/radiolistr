import pandas as pd
import re
from tempfile import NamedTemporaryFile
from os import remove

def read_xls_or_csv(f, name):
	if name.lower().endswith('.xls'):
		d = pd.read_excel(f)
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
	outdf.to_excel(path, columns=cols,
		header=map(lambda s: s.title(), ldf.columns),
		index=False, encoding='utf8')
	return path

def json2df(data):
	return pd.read_json(data, orient='records')

def df2json(df):
	return df.to_json(orient='records', force_ascii=False)

def table2json(f, path):
	return df2json(find_columns(read_xls_or_csv(f, path)))

def fixtimefn(time):
	if isinstance(time, float):
		return time
	else:
		m, s = time.split(':')
		return float(m) + float(s)/100.0

def fixtime(df, col):
	df[col] = df[col].map(fixtimefn)

#outtf = NamedTemporaryFile(mode='w+b', suffix='xls', delete=False)

