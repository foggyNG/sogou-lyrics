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

## @package RBLyrics.engine.lrcbase
#  歌词下载引擎基类。

import rb, logging
from chardet import detect
from ..utils import distance, LyricsInfo
log = logging.getLogger('RBLyrics')

## 歌词下载引擎基类。
class LRCBase:
	
	## 构造函数。
	#  @param songinfo 歌曲信息。
	#  @param auto 是否自动匹配歌词。
	#  @param max 最大尝试次数。
	def __init__(self, songinfo, auto, max):
		self._songinfo = songinfo
		self._auto = auto
		self._max = max
		self._candidate = []
		self._job = []
		return
	
	## 歌词收取响应函数。
	#  @param cache 歌词原始文本。
	#  @param callback 线程回调函数。
	def _on_lyrics_arrive(self, cache, callback):
		if cache is None:
			callback(self.__class__.__name__, self._candidate)
		else:
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
			l = LyricsInfo(cache)
			d = distance(self._songinfo, l)
			self._candidate.append([d, l])
			if self._auto and d == 0:
				callback(self.__class__.__name__, self._candidate)
			else:
				self._get_next_lyrics(callback)
		return
	
	## 获取下一个歌词。
	#  @param callback 线程回调函数。
	def _get_next_lyrics(self, callback):
		if len(self._job) > 0:
			url = self._job.pop(0)
			log.info('%s <%s>' % (self.__class__.__name__, url))
			rb.Loader().get_url(url, self._on_lyrics_arrive, callback)
		else:
			callback(self.__class__.__name__, self._candidate)
		return
			
