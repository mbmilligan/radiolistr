import requests
import json
from lxml import html
import sys
import time
import re
from fuzzywuzzy import fuzz as fuzz, utils as fwutils, process as fwproc

DATAENC = 'utf-8'
USER_AGENT = "radiolistr/2019 +github.com/mbmilligan/radiolistr"

def init_session(user_agent=USER_AGENT):
	s = requests.Session()
	s.headers.update({'User-Agent': user_agent})
	return s

def justtext(element):
	return html.tostring(element, method='text', encoding='unicode').strip()

def albumsearch(artist, release, session=None):
	if not session:
		session = init_session()
	page = session.get('http://www.metal-archives.com/search/ajax-advanced/searching/albums/', 
						params={ 'bandName': artist, 'releaseTitle': release })
	page.encoding = DATAENC
	data = json.loads(page.text)
	try:
		addr = html.fromstring( data['aaData'][0][1] ).xpath('a')[0].values()[0]
	except:
		addr = None
	return addr

def extractalbumdata(pagetext):
	tree = html.fromstring( pagetext )
	ret = {}
	ret['album'] = justtext(tree.xpath('//h1[@class="album_name"]')[0])
	ret['artist'] = justtext(tree.xpath('//h2[@class="band_name"]')[0])
	ret['label'] = justtext(tree.xpath('//dl/dt[text()="Label:"]/following::dd[1]')[0])
	ret['date'] = justtext(tree.xpath('//dl/dt[text()="Release date:"]/following::dd[1]')[0])
	tracklist = []
	tracks = tree.xpath('//table[contains(@class,"table_lyrics")]')[0]
	for row in tracks.xpath('*/tr[@class="even" or @class="odd"]'):
		tds = row.findall('td')
		for i, td in enumerate(tds):
			if td.attrib.get('class') == 'wrapWords':
				tracklist.append([ justtext(td), justtext(tds[i+1]) ])
				break
	ret['tracks'] = tracklist
	return ret

def getalbumdata(artist, release, session=None):
	if not session:
		session = init_session()
	addr = albumsearch(artist, release)
	ret = {'artist': artist, 'album': release}
	if addr: ret['url'] = addr
	try:
		page = session.get(addr)
		page.encoding = DATAENC
		ret.update(extractalbumdata(page.text))
	except:
		pass
	return ret

def gettrackdata(artist, release, track=None):
	data = getalbumdata(artist, release)
	if not track or len(data['tracks']) < 1:
		return data
	match, score = fwproc.extractOne(track, data['tracks'],
				  processor=lambda e: unicode(e[0],DATAENC),
				  scorer=fuzz.UWRatio)
	if score >= 88:
		data['tracks'] = [ match ]
	return data

def printlabels():
	for line in sys.stdin.readlines():
		a, t, r = line.split('\t')
		label = getalbumdata(a, r).get('label', 'NOT FOUND')
		print(label)
		time.sleep(0.1)

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1].endswith('debug'):
		for l in sys.stdin.readlines():
			a, t, r = l.split('\t')
			print(getalbumdata(a, r))
	printlabels()

def bandsearch(params, activeOnly=False, session=None):
	"""Submit advanced search by bands
	Valid parameters seem to be:
	bandName=
	exactBandMatch (=1 if desired)
	genre=
	country=
	yearCreationFrom=
	yearCreationTo=
	status= (1 = active, other values unknown)
	themes=
	location=
	bandLabelName=
	indieLabel (=1 if desired)
	"""
	if not session:
		session = init_session()
	url = 'http://www.metal-archives.com/search/ajax-advanced/searching/bands/'
	if activeOnly: params['status'] = 1
	data = json.loads(session.get(url, params=params).text)
	data['bands'] = []
	for be in data['aaData']:
		a = html.fromstring(be[0]).find('a')
		data['bands'].append(
			{ 'name' : a.text,
			  'url'  : a.get('href'),
			  'genre': be[1],
			  'location': be[3] }
			)
	return data

def id_from_url(url):
	comps = url.split('/')
	comps.reverse()
	for c in comps:
		if re.match('^[0-9]+$', c):
			return c

def discog_by_id(idnum, session=None):
	if not session:
		session = init_session()
	ids = str(idnum)
	url = 'http://www.metal-archives.com/band/discography/id/%s/tab/all' % (ids,)
	return session.get(url).text

def discog_parse(table):
	tab = html.fromstring(table).find('tbody')
	dl = []
	for td in tab.findall('tr'):
		try:
			dl.append(
			  { 'url' : td[0][0].get('href'),
				'name': td[0][0].text,
				'type': td[1].text,
				'year': td[2].text }
			)
		except:
			pass
	return dl

def _discsortkey(disc):
	k2 = {'Full-length': '900', 'EP': '500'}.get(disc['type'], '100')
	k1 = disc['year']
	k3 = id_from_url(disc['url'])
	return k1 + k2 + k3

def discog_latest_release(discs):
	dl = sorted(discs, key=_discsortkey, reverse=True)
	if len(dl) > 0: return dl[0]
	else: return None

def discog_significant_releases(discs):
	"""Selects interesting releases from full table returned by discog_parse()

	Example of finding album release dates in bulk:

	with open('../iconic.csv','r',newline='') as f:
	  with open('../iconic_dates.csv','a',newline='') as o:
	    cr = csv.reader(f)
	    co = csv.DictWriter(o, ['artist','album','date'], extrasaction='ignore')
	    cr = [ y for (x,y) in enumerate(cr) if y[1].startswith('http') ]
	    start = False
	    for row in cr:
	        artist, url = row[0:2]
	        rels = met.discog_significant_releases(
	          met.discog_parse(met.discog_by_id(met.id_from_url(url), session=s))
	          )
	        for r in rels:
	            sleep(0.2)
	            if r['url'].find('Edenbridge/Soli') > 0:
	                start = True
	            if not start:
	                continue
	            rel = met.extractalbumdata(s.get(r['url']).text)
	            print(rel['artist'],rel['album'])
	            co.writerow(rel)

	Note that the dateparser module can be useful for reading long-form dates:

		dt = dateparser.parse(date, settings={'PREFER_DAY_OF_MONTH': 'first'})
		tt = dt.timetuple()
		co.writerow([artist, album, date, tt.tm_year, tt.tm_yday])

	"""
	return [ y for (x,y) in enumerate(discs) if x == 0 or
		y['type'] in ('Full-length', 'EP') ]
