#!/usr/bin/env python
#-*- coding: UTF-8 -*-

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

import re, cookielib, urllib2, sys

from RBLyrics.chardet import detect
from RBLyrics.utils import log, clean_token, distance, LyricsInfo, SongInfo

## Sogou mp3 engine.
#
#  Retrieve lyrics from mp3.sogou.com.
class Sogou:
	
	## @var _timeout
	#  HTTP request timeout.
	
	## @var _max
	#  Max number of lyrics expected.
	
	## The constructor.
	#  @param timeout HTTP request timeout.
	#  @param max Max number of lyrics expected.
	def __init__(self, timeout = 3, max = 5):
		log.debug('enter')
		self._timeout = timeout
		self._max = max
		log.debug('leave')
		return
	
	## Retrieve lyrics.
	#  @param songinfo Song information.
	#  @return Lyrics candidate list.
	def search(self, songinfo):
		log.debug('enter')
		retval = []
		token = clean_token(songinfo.get('ti'))
		encoding = detect(token)['encoding']
		title_encode = urllib2.quote(token.decode(encoding, 'ignore').encode('GBK', 'ignore'))
		token = clean_token(songinfo.get('ar'))
		encoding = detect(token)['encoding']
		artist_encode = urllib2.quote(token.decode(encoding, 'ignore').encode('GBK', 'ignore'))
		url = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_encode, title_encode)
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
						for line in cache:
							m = re.search('downlrc\.jsp\?[^\"]*', line)
							if m != None:
								url = 'http://mp3.sogou.com/%s' % m.group(0)
								try:
									cache = opener.open(url, None, self._timeout).read()
								except Exception as e:
									log.error(e)
								else:
									encoding = detect(cache)['encoding']
									cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
									lyrics = LyricsInfo(cache)
									dist = distance(songinfo, lyrics)
									log.info('[score = %d] <%s>' % (dist, url))
									retval.append([dist, lyrics])
									if dist == 0 or len(retval) >= self._max:
										break
						log.info('%d candidates found' % len(retval))
					break
			else:
				log.info('0 candidates found')
		log.debug('leave')
		return retval
