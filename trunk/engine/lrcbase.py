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
import rb, logging
from chardet import detect

log = logging.getLogger('RBLyrics')

## Lyricist engine.
#
#  Retrieve lyrics from www.winampcn.com.
class LRCBase:
	
	## The constructor.
	#  @param timeout HTTP request timeout.
	#  @param max Max number of lyrics expected.
	def __init__(self, artist, title, receiver, max):
		self._artist = artist
		self._title = title
		self._receiver = receiver
		self._max = max
		self._job = []
		return
	
	def _on_lyrics_arrive(self, cache, callback, engine_name):
		if cache is None:
			# rb.Loader failed, stop the engine
			self._receiver(cache)
			callback(engine_name)
		else:
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
			if self._receiver(cache):
				self._get_next_lyrics(callback, engine_name)
			else:
				self._receiver(None)
				callback(engine_name)
		return
		
	def _get_next_lyrics(self, callback, engine_name):
		log.debug('%s, %d jobs left' % (engine_name, len(self._job)))
		if len(self._job) > 0:
			url = self._job.pop(0)
			log.info('%s <%s>' % (engine_name, url))
			rb.Loader().get_url(url, self._on_lyrics_arrive, callback, engine_name)
		else:
			self._receiver(None)
			callback(engine_name)
		return
			
