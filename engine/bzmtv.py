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

## @package RBLyrics.engine.bzmtv
#  Bzmtv歌词下载引擎。

import rb, urllib, re, logging
from xml.dom.minidom import parseString
from chardet import detect
from lrcbase import LRCBase
log = logging.getLogger('RBLyrics')

## Bzmtv歌词下载引擎。
class Bzmtv(LRCBase):
	
	## 构造函数。
	#  @param artist 艺术家。
	#  @param title 标题。
	#  @param receiver 歌词回调函数。
	#  @param max 最大尝试次数。
	def __init__(self, artist, title, receiver, max = 5):
		LRCBase.__init__(self, artist, title, receiver, max)
		return
	
	## 搜索页响应函数。
	#  @param cache 得到的响应文本。
	#  @param callback 线程回调函数。
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
				log.debug('%d jobs found' % len(self._job))
				self._get_next_lyrics(callback)
		return
	
	## 开始搜索。
	#  @param callback 线程回调函数。
	def search(self, callback):
		title_token = self._title.encode('GBK', 'ignore')
		urldata = {'key':title_token, 'go':'go', 'y':1}
		url = 'http://lrc.bzmtv.com/So.asp?%s' % urllib.urlencode(urldata)
		log.debug('search url <%s>' % url)
		rb.Loader().get_url(url, self._on_meta_arrive, callback)
		return
			
