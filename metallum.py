import requests
import json
from lxml import html
import sys
import time
import re
from fuzzywuzzy import fuzz as fuzz, utils as fwutils, process as fwproc

DATAENC = 'utf-8'

def justtext(element):
	return html.tostring(element, method='text', encoding=DATAENC).strip()

def albumsearch(artist, release):
	page = requests.get('http://www.metal-archives.com/search/ajax-advanced/searching/albums/', 
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

def getalbumdata(artist, release):
	addr = albumsearch(artist, release)
	ret = {'artist': artist, 'album': release}
	if addr: ret['url'] = addr
	try:
		page = requests.get(addr)
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
		print label 
		time.sleep(0.1)

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1].endswith('debug'):
		for l in sys.stdin.readlines():
			a, t, r = l.split('\t')
			print getalbumdata(a, r)
	printlabels()

def bandsearch(params, activeOnly=False):
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
	url = 'http://www.metal-archives.com/search/ajax-advanced/searching/bands/'
	if activeOnly: params['status'] = 1
	data = json.loads(requests.get(url, params=params).text)
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

def discog_by_id(idnum):
	ids = str(idnum)
	url = 'http://www.metal-archives.com/band/discography/id/%s/tab/all' % (ids,)
	return requests.get(url).text

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
