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

## @package RBLyrics.engine.minilyrics
#  Minilyrics search engine.

import urllib2, logging, threading
from hashlib import md5
from xml.dom.minidom import parseString
from optparse import OptionParser

from chardet import detect
log = logging.getLogger('RBLyrics')

## TTPlayer engine.
#
#  Retrieve lyrics from www.viewlyrics.com.
class Minilyrics:
	
	## @var _timeout
	#  HTTP request timeout.
	
	## @var _max
	#  Max number of lyrics expected.
	
	## @var _candidate
	#  Lyrics candidates.
	
	## @var _lock
	#  Thread lock for appending _candidate list.
	
	## The constructor.
	#  @param timeout HTTP request timeout.
	#  @param max Max number of lyrics expected.
	def __init__(self, timeout = 3, max = 5):
		log.debug('enter')
		self._timeout = timeout
		self._max = max
		self._candidate = []
		self._lock = threading.Condition(threading.Lock())
		log.debug('leave')
		return
	
	## Lyrics receive handler.
	#  @param url Lyrics url.
	def _receive_lyrics(self, url):
		log.debug('enter')
		try:
			cache = urllib2.urlopen(url, None, self._timeout).read()
		except Exception as e:
			log.error(e)
		else:
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
			log.info('lyrics <%s>' % url)
			self._lock.acquire()
			self._candidate.append(cache)
			self._lock.release()
		log.debug('leave')
		return
		
	## Retrieve lyrics.
	#  @param artist Song artist.
	#  @param title Song title.
	#  @return Lyrics candidates.
	def search(self, artist, title):
		log.debug('enter')
		retval = []
		artist_token = urllib2.quote(artist)
		title_token = urllib2.quote(title)
		xml = "<?xml version=\"1.0\" encoding='utf-8'?>\r\n"
		xml += "<search filetype=\"lyrics\" artist=\"%s\" title=\"%s\" " % (artist_token, title_token)
		xml += "ClientCharEncoding=\"utf-8\"/>\r\n"
		m = md5()
		m.update(xml + 'Mlv1clt4.0')
		request = '\x02\x00\x04\x00\x00\x00%s%s' % (m.digest(), xml)
		url = 'http://www.viewlyrics.com:1212/searchlyrics.htm'
		try:
			xml = urllib2.urlopen(url, request, self._timeout).read()
		except Exception as e:
			log.error(e)
		else:
			elements = parseString(xml).getElementsByTagName('fileinfo')
			threads = []
			for element in elements:
				url = element.getAttribute('link')
				threads.append(threading.Thread(target=self._receive_lyrics, args=(url,)))
				if len(threads) >= self._max:
					break
			for t in threads:
				t.start()
			for t in threads:
				t.join()
			log.info('%d candidates found' % len(self._candidate))
		log.debug('leave')
		return self._candidate

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
		engine = Minilyrics(options.timeout, options.max)
		candidate = engine.search(options.artist, options.title)
		for c in candidate:
			log.info('candidate:\n%s' % c)
			
