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

import rb, urllib, re, logging
from xml.dom.minidom import parseString
from chardet import detect

from lrcbase import LRCBase
log = logging.getLogger('RBLyrics')

## Lyricist engine.
#
#  Retrieve lyrics from www.winampcn.com.
class Bzmtv(LRCBase):
	
	## The constructor.
	#  @param timeout HTTP request timeout.
	#  @param max Max number of lyrics expected.
	def __init__(self, artist, title, receiver, max = 5):
		LRCBase.__init__(self, artist, title, receiver, max)
		return
		
	def _on_meta_arrive(self, cache, callback):
		if cache is None:
			log.warn('network error')
			# the following code make sure the main Engine to quit normally
			self._receiver(None)
			callback(self.__class__.__name__)
		else:
			try:
				encoding = detect(cache)['encoding']
				cache = cache.decode(encoding, 'ignore').splitlines()
			except Exception, e:
				log.error(e)
				# the following code make sure the main Engine to quit normally
				self._receiver(None)
				callback(self.__class__.__name__)
			else:
				pattern = re.compile(r'<div class="slczt"><a  href="(?P<lrc>[^"]+?)" target=_blank><img border=0 src=img/lrc.gif></A></div>')
				for line in cache:
					for seg in pattern.findall(line):
						self._job.append('http://lrc.bzmtv.com/%s' % seg)
						if len(self._job) >= self._max:
							break
					if len(self._job) >= self._max:
							break
				log.debug('%d lyrics url found' % len(self._job))
				self._get_next_lyrics(callback, self.__class__.__name__)
		return
		
	def search(self, callback):
		title_token = self._title.encode('GBK', 'ignore')
		urldata = {'key':title_token, 'go':'go', 'y':1}
		url = 'http://lrc.bzmtv.com/So.asp?%s' % urllib.urlencode(urldata)
		log.debug('search url <%s>' % url)
		rb.Loader().get_url(url, self._on_meta_arrive, callback)
		return
			
