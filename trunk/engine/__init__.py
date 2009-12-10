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

## @package RBLyrics.engine
#  歌词下载模块。

import rb, logging, sys
from chardet import detect

from sogou import Sogou
from ttplayer import TTPlayer
from lyricist import Lyricist
from jpwy import Jpwy
from bzmtv import Bzmtv
from utils import clean_token, distance, LyricsInfo
log = logging.getLogger('RBLyrics')

## 歌词搜索引擎。
engine_map = {
	'engine.sogou' : Sogou,
	'engine.bzmtv' : Bzmtv,
	'engine.jpwy' : Jpwy,
	'engine.ttplayer' : TTPlayer,
	'engine.lyricist': Lyricist
}

def candidate_cmp(x, y):
	return x[0] - y[0]

## 歌词下载启动器。
class Engine:
	
	## 构造函数。
	#  @param engine 歌词引擎列表。
	#  @param songinfo 歌曲信息。
	#  @param callback 下载回调函数。
	#  @param auto 是否自动选择歌词。
	def __init__(self, engine, songinfo, callback, auto):
		self._engine = engine
		self._songinfo = songinfo
		self._callback = callback
		self._candidate = []
		self._auto = auto
		return
	
	## 启动搜索引擎。
	def _searcher(self, plexer):
		log.debug('search begin <%s>' % str(self._songinfo))
		for key in self._engine:
			plexer.clear()
			engine = engine_map[key](self._songinfo, self._auto)
			engine.search(plexer.send())
			yield None
			_, (engine_name, candidate) = plexer.receive()
			log.debug('%s finished' % engine_name)
			self._candidate += candidate
			if self._auto:
				found = False
				for c in candidate:
					if c[0] == 0:
						found = True
						break
				if found:
					break
		self._candidate.sort(candidate_cmp)
		self._callback(self._songinfo, self._candidate, self._auto)
		log.debug('search finished <%s>' % str(self._songinfo))
		return
	
	## 开始搜索。
	def search(self):
		rb.Coroutine(self._searcher).begin()
		return
