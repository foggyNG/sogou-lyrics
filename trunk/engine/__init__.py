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
		# if lyrics with distance=0 found
		self._found = False
		self._auto = auto
		# number of working lyrics engines
		self._alive = 0
		return
	
	## 歌词收取响应函数。
	#  @param raw 得到的歌词原始文本。
	#  @return 是否继续下载。
	def on_lyrics_arrive(self, raw):
		ret = False
		if raw == None:
			# while rb.Loader failed or finished
			self._alive -= 1
		elif self._found:
			# while lyrics already found
			self._alive -= 1
		else:
			# upcoming raw should be processed
			l = LyricsInfo(raw)
			d = distance(self._songinfo, l)
			self._candidate.append([d, l])
			self._found = (self._auto and (d == 0))
			if self._found:
				# upcoming raw distance=0
				self._candidate.sort(candidate_cmp)
				self._callback(self._songinfo, self._candidate, self._auto)
				self._alive -= 1
			else:
				# continue to next lyrics
				ret = True
		if self._alive == 0 and not self._found:
			self._candidate.sort(candidate_cmp)
			self._callback(self._songinfo, self._candidate, self._auto)
		return ret
	
	## 启动搜索引擎。
	def _searcher(self, plexer):
		token = clean_token(self._songinfo.ar)
		encoding = detect(token)['encoding']
		artist = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
		token = clean_token(self._songinfo.ti)
		encoding = detect(token)['encoding']
		title = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
		if artist == clean_token('Unknown'):
			artist = ''
		self._alive = len(self._engine)
		if self._alive == 0:
			# no engine selected
			self._callback(self._songinfo, self._candidate, self._auto)
		else:
			for key in self._engine:
				plexer.clear()
				engine = engine_map[key](artist, title, self.on_lyrics_arrive)
				engine.search(plexer.send())
				yield None
				_, (engine_name,) = plexer.receive()
				log.debug('%s finished' % engine_name)
		return
	
	## 开始搜索。
	def search(self):
		rb.Coroutine(self._searcher).begin()
		return
