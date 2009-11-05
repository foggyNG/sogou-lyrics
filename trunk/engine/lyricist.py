#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

import urllib2, re, sys
from xml.dom.minidom import parseString

from RBLyrics.chardet import detect
from RBLyrics.utils import log, clean_token, distance, LyricsInfo, SongInfo

## Lyricist engine.
#
#  Retrieve lyrics from www.winampcn.com.
class Lyricist:
	
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
	
	## Clean special characters.
	#  @param token Original token.
	#  @return Cleaned token.
	def _clean_token(self, token):
		return re.sub('[\ \t~`!@#$%\^&*\(\)-_+=|\\\{\}\[\]:\";\'<>\?,\./]', '', token)
	
	## Retrieve lyrics.
	#  @param songinfo Song information.
	#  @return Lyrics candidate list.
	def search(self, songinfo):
		log.debug('enter')
		retval = []
		token = self._clean_token(clean_token(songinfo.get('ti')))
		encoding = detect(token)['encoding']
		title_token = urllib2.quote(token.decode(encoding, 'ignore').encode('UTF-8', 'ignore'))
		token = self._clean_token(clean_token(songinfo.get('ar')))
		encoding = detect(token)['encoding']
		artist_token = urllib2.quote(token.decode(encoding, 'ignore').encode('UTF-8', 'ignore'))
		url = 'http://www.winampcn.com/lrceng/get.aspx?song=%s&artist=%s&lsong=%s&prec=1&Datetime=20060601' % (title_token, artist_token, title_token)
		log.debug('search url <%s>' % url)
		try:
			xml = urllib2.urlopen(url, None, self._timeout).read()
		except Exception as e:
			log.error(e)
		else:
			elements = parseString(xml).getElementsByTagName('LyricUrl')
			for element in elements:
				url = element.firstChild.data
				try:
					cache = urllib2.urlopen(url, None, self._timeout).read()
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
		log.debug('leave')
		return retval
