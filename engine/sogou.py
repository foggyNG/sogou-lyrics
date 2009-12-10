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
#  搜狗歌词下载引擎。

import rb, urllib, re, logging
from xml.dom.minidom import parseString
from chardet import detect
from ..utils import clean_token
from lrcbase import LRCBase
log = logging.getLogger('RBLyrics')

## 搜狗歌词下载引擎。
class Sogou(LRCBase):
	
	## 构造函数。
	#  @param songinfo 歌曲信息。
	#  @param auto 是否自动匹配歌词。
	#  @param max 最大尝试次数。
	def __init__(self, songinfo, auto, max = 5):
		LRCBase.__init__(self, songinfo, auto, max)
		return
	
	## 歌词页响应函数。
	#  @param cache 得到的响应文本。
	#  @param callback 线程回调函数。
	def _on_lyrics_page_arrive(self, cache, callback):
		try:
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').splitlines()
		except Exception, e:
			log.warn(e)
			callback(self.__class__.__name__, self._candidate)
		else:
			pattern = re.compile(r'<a href="downlrc\.jsp\?(?P<url>[^"]+?)">')
			for line in cache:
				for seg in pattern.findall(line):
					self._job.append('http://mp3.sogou.com/downlrc.jsp?%s' % seg)
					if len(self._job) >= self._max:
						break
				if len(self._job) >= self._max:
						break
			log.debug('%d jobs found' % len(self._job))
			self._get_next_lyrics(callback)
		return
	
	## 搜索页响应函数。
	#  @param cache 得到的响应文本。
	#  @param callback 线程回调函数。
	def _on_search_page_arrive(self, cache, callback):
		try:
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').splitlines()
		except Exception, e:
			log.warn(e)
			callback(self.__class__.__name__, self._candidate)
		else:
			pattern = re.compile(r'onclick="dyama\(\'gecd?i\'\);" href="(?P<url>[^"]+?)"')
			for line in cache:
				seg = pattern.findall(line)
				if len(seg):
					url = 'http://mp3.sogou.com' + seg[0]
					log.debug('lyrics page url <%s>' % url)
					rb.Loader().get_url(url, self._on_lyrics_page_arrive, callback)
					break
			else:
				log.debug('lyrics page not found')
				callback(self.__class__.__name__, self._candidate)
		return
	
	## 开始搜索。
	#  @param callback 线程回调函数。
	def search(self, callback):
		artist = clean_token(self._songinfo.ar)
		if artist == clean_token('Unknown'):
			artist = ''
		title = clean_token(self._songinfo.ti)
		artist_token = urllib.quote(artist.encode('GBK', 'ignore'))
		title_token = urllib.quote(title.encode('GBK', 'ignore'))
		if len(artist_token) > 0:
			url = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_token, title_token)
		else:
			url = 'http://mp3.sogou.com/music.so?query=%s' % title_token
		log.debug('search url <%s>' % url)
		rb.Loader().get_url(url, self._on_search_page_arrive, callback)
		return
			
		
