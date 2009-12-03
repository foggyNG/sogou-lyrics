#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#
#       
#       Copyright 2009 wonder <gogo.wonder@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

## @package RBLyrics.engine.lyricist
#  Lyricist search engine.

import urllib, urllib2, re, logging, threading
from xml.dom.minidom import parseString
from optparse import OptionParser
from chardet import detect

log = logging.getLogger('RBLyrics')

## Lyricist engine.
#
#  Retrieve lyrics from www.winampcn.com.
class Jpwy(threading.Thread):
	
	## The constructor.
	#  @param timeout HTTP request timeout.
	#  @param max Max number of lyrics expected.
	def __init__(self, artist, title, receiver, timeout = 3, max = 5):
		threading.Thread.__init__(self)
		self._artist = artist
		self._title = title
		self._receiver = receiver
		self._timeout = timeout
		self._max = max
		return
		
	## Retrieve lyrics.
	#  @param artist Song artist.
	#  @param title Song title.
	#  @return Lyrics candidates.
	def run(self):
		log.debug('enter')
		artist_token = self._artist.encode('GBK', 'ignore')
		title_token = self._title.encode('GBK', 'ignore')
		urldata = urllib.urlencode({'singer':artist_token, 'song':title_token})
		url = 'http://www.jpwy.net/gc/search.php'
		log.debug('search url <%s?%s>' % (url, urldata))
		try:
			cache = urllib2.urlopen(url, urldata, self._timeout).read()
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').splitlines()
		except Exception as e:
			log.error(e)
		else:
			pattern = re.compile(r'<[Aa] href="(?P<url>[^"]+?)"><img border=0 src=http://ww.jpwy.net/gc/image/lrc.gif>')
			urls = []
			for line in cache:
				urls += pattern.findall(line)
			for url in urls:
				try:
					cache = urllib2.urlopen(url, None, self._timeout).read()
				except Exception as e:
					log.error(e)
				else:
					encoding = detect(cache)['encoding']
					cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
					log.info('lyrics <%s>' % url)
					if self._receiver(cache) or urls.index(url) >= self._max:
						break
		log.debug('leave')
		return

def console_receiver(raw):
	log.info('candidate:\n%s' % raw.decode('UTF-8', 'ignore'))
	return False
	
if __name__ == '__main__':
	log.setLevel(logging.DEBUG)
	handler = logging.StreamHandler()
	handler.setFormatter(logging.Formatter('%(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
	log.addHandler(handler)
	parser = OptionParser()
	parser.add_option('-a', '--artist', dest = 'artist', type = 'string', help = 'song artist')
	parser.add_option('-i', '--title', dest = 'title', type = 'string', help = 'song title')
	parser.add_option('-t', '--timeout', dest = 'timeout', type = 'int', help = 'url request timeout')
	parser.add_option('-m', '--max', dest = 'max', type = 'int', help = 'max number of expected')
	parser.set_defaults(timeout = 3, max = 5)
	(options, args) = parser.parse_args()
	if len(args) != 0:
		parser.error("incorrect number of arguments")
	elif options.artist is None:
		parser.error('artist is required')
	elif options.title is None:
		parser.error('title is required')
	else:
		engine = Jpwy(options.artist, options.title, console_receiver, options.timeout, options.max)
		engine.start()
		engine.join()
			
			
