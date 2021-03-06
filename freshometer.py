import json, urllib, time, threading, re, webbrowser, random
from pyquery import PyQuery as pq

class Freshometer:

	config = {}
	indexer = {}

	def __init__(self):
		self.loadConfig()
		self.indexer = Indexer(self.config)

		self.readSites()
		print('Indexing completed.')

		results = self.querySites()
		for result in results:
			print(result['text'] + ' || ' + result['sanitizedUrl'] + ' || ' + result['source'])
			if self.config['browser'] and result['sanitizedUrl']:
				webbrowser.open(result['sanitizedUrl'])
		
		print('Query completed.')

	def loadConfig(self):
		json_data = open('config.json').read()
		self.config = json.loads(json_data)

	def readSites(self):
		for site in self.config['sites']:
			SiteIndexThread(site, self.indexer).start()

		while(threading.activeCount()>1):
			1==1

	def querySites(self):
		return self.indexer.query()

class SiteIndexThread (threading.Thread):

	indexer = {}
	site = {}

	def __init__(self, site, indexer):
		threading.Thread.__init__(self)
		self.site = site
		self.indexer = indexer

	def run(self):
		self.indexer.index(self.readLinks())

	def readLinks(self):
		try:
			site = pq(self.site['url'])
		except:
			print ("Failed loading " + self.site['url'])
			return []

		selections = site(self.site['selector'])
		links = []
		for i in range(0, len(selections)):
			link_data = {}
			link_data['url'] = selections.eq(i).attr('href')
			link_data['sanitizedUrl'] = sanitizeLink(link_data['url'])
			link_data['text'] = selections.eq(i).text()
			link_data['date'] = int(time.time())
			link_data['source'] = self.site['url']
			links.append(link_data)

		return links

class Indexer:

	config = {}
	links = []

	def __init__(self, config):
		self.config = config

	def index(self, new_links):
		self.links.extend(new_links)

	def query(self):
		results = []
		resultUrls = []

		for i in range(0, len(self.links)):
			if self.links[i]['sanitizedUrl'] in resultUrls:
				continue
			for keyword in self.config['keywords']:
				if  keyword.lower() in self.links[i]['text'].lower():
					results.append(self.links[i])
					resultUrls.append(self.links[i]['sanitizedUrl'])
					break
		random.shuffle(results)
		
		return results[0:self.config['results']]

def sanitizeLink(raw_link):
	if None == raw_link:
		return ''
	decoded = urllib.unquote(urllib.unquote(raw_link))
	linkMatch = re.search(r"(https?\:\/\/.*)", decoded)
	if linkMatch:
		return linkMatch.group(0)
	return ''

f = Freshometer()

