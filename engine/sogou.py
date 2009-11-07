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

## @package RBLyrics.engine.sogou
#  Sogou search engine.

import re, cookielib, urllib2, logging, threading
from optparse import OptionParser

from chardet import detect
log = logging.getLogger('RBLyrics')

## Sogou mp3 engine.
#
#  Retrieve lyrics from mp3.sogou.com.
class Sogou:
	
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
	#  @param opener Cookie opener.
	#  @param url Lyrics url.
	def _receive_lyrics(self, opener, url):
		log.debug('enter')
		try:
			cache = opener.open(url, None, self._timeout).read()
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
		artist_token = urllib2.quote(artist.encode('GBK', 'ignore'))
		title_token = urllib2.quote(title.encode('GBK', 'ignore'))
		url = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_token, title_token)
		log.debug('search page <%s>' % url)
		try:
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			cache = opener.open(url, None, self._timeout).read()
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').splitlines()
		except Exception as e:
			log.error(e)
		else:
			for line in cache:
				# grab lyrics search page, only use the first
				m = re.search('geci\.so\?[^\"]*', line)
				if m != None:
					url = 'http://mp3.sogou.com/%s' % m.group(0)
					log.debug('lyrics page <%s>' % url)
					try:
						cache = opener.open(url, None, self._timeout).read()
						encoding = detect(cache)['encoding']
						cache = cache.decode(encoding, 'ignore').splitlines()
					except Exception as e:
						log.error(e)
					else:
						# grab lyrics file url, try all of them
						threads = []
						for line in cache:
							m = re.search('downlrc\.jsp\?[^\"]*', line)
							if m != None:
								url = 'http://mp3.sogou.com/%s' % m.group(0)
								threads.append(threading.Thread(target=self._receive_lyrics, args=(opener, url,)))
								if len(threads) >= self._max:
									break
						for t in threads:
							t.start()
						for t in threads:
							t.join()
						log.info('%d candidates found' % len(self._candidate))
					break
			else:
				log.info('0 candidates found')
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
		engine = Sogou(options.timeout, options.max)
		candidate = engine.search(options.artist, options.title)
		for c in candidate:
			log.info('candidate:\n%s' % c)
			
		
