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
from utils import LyricsInfo, distance, clean_token

log = logging.getLogger('RBLyrics')

## Sogou mp3 engine.
#
#  Retrieve lyrics from mp3.sogou.com.
class Sogou(threading.Thread):
	
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
		threading.Thread.__init__(self)
		self._stopevent = threading.Event()
		self._timeout = timeout
		self._max = max
		self._songinfo = None
		self._candidate = []
		log.debug('leave')
		return
	
	## Lyrics receive handler.
	#  @param opener Cookie opener.
	#  @param url Lyrics url.
	def _get_lyrics(self, opener, url):
		log.debug('enter')
		try:
			cache = opener.open(url, None, self._timeout).read()
		except Exception as e:
			log.error(e)
		else:
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
			log.info('lyrics <%s>' % url)
			lyrics = LyricsInfo(cache)
			ret = distance(self._songinfo, lyrics)
			self._candidate.append([ret, lyrics])
		log.debug('leave')
		return
		
	## Retrieve lyrics.
	#  @param artist Song artist.
	#  @param title Song title.
	#  @return Lyrics candidates.
	def search(self, songinfo):
		log.debug('enter')
		self._songinfo = songinfo
		self.start()
		log.debug('leave')
		return
	
	def run(self):
		artist_token = urllib2.quote(clean_token(self._songinfo.get('ar')).encode('GBK', 'ignore'))
		title_token = urllib2.quote(clean_token(self._songinfo.get('ti')).encode('GBK', 'ignore'))
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
								if self._stopevent.is_set():
									log.warn('stopped')
									break
								url = 'http://mp3.sogou.com/%s' % m.group(0)
								distance = self._get_lyrics(opener, url)
								if len(self._candidate) >= self._max or distance <= 0:
									break
						log.info('%d candidates found' % len(self._candidate))
					break
			else:
				log.info('0 candidates found')
			return
	def stop(self):
		log.debug('enter')
		self._stopevent.set()
		log.debug('leave')
		return
		
	def candidate(self):
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
		candidate = engine.search(options.artist.decode('UTF-8', 'ignore'), options.title.decode('UTF-8', 'ignore'))
		for c in candidate:
			log.info('candidate:\n%s' % c.decode('UTF-8', 'ignore'))
			
		
