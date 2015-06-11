import requests
import json
from lxml import html
import sys
import time
import re

def albumsearch(artist, release):
	page = requests.get('http://www.metal-archives.com/search/ajax-advanced/searching/albums/', 
						params={ 'bandName': artist, 'releaseTitle': release })
	data = json.loads(page.text)
	try:
		addr = html.fromstring( data['aaData'][0][1] ).xpath('a')[0].values()[0]
	except:
		addr = None
	return addr

def getalbumdata(artist, release):
	addr = albumsearch(artist, release)
	ret = {'artist': artist, 'release': release}
	if addr: ret['url'] = addr
	try:
		tree = html.fromstring( requests.get(addr).text )
		ret['release'] = tree.xpath('//h1[@class="album_name"]//text()')[0]
		ret['artist'] = tree.xpath('//h2[@class="band_name"]//text()')[0]
		ret['label'] = tree.xpath('//dl[@class="float_right"]/dt[text()="Label:"]/following::dd[1]//text()')[0]
	except:
		pass
	return ret

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
