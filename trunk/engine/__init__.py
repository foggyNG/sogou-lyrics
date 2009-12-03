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
#  Lyrics search engine.

import threading, sys
from chardet import detect

from sogou import Sogou
from ttplayer import TTPlayer
from minilyrics import Minilyrics
from lyricist import Lyricist
from jpwy import Jpwy
from bzmtv import Bzmtv
from utils import log, clean_token, distance, LyricsInfo, save_lyrics

## Lyrics search engine map.
engine_map = {
	'engine.bzmtv' : Bzmtv,
	'engine.jpwy' : Jpwy,
	'engine.ttplayer' : TTPlayer,
	'engine.sogou' : Sogou,
	'engine.minilyrics': Minilyrics,
	'engine.lyricist': Lyricist
}

## Lyrics candidate comparison handler.
def candidate_cmp(x, y):
	return x[0] - y[0]

## Lyrics search engine manager.
class Engine(threading.Thread):
	
	## The constructor.
	#  @param engine Engine list.
	#  @param songinfo Song information.
	def __init__(self, engine, songinfo, callback):
		threading.Thread.__init__(self)
		self._engine = engine
		self._songinfo = songinfo
		self._callback = callback
		self._candidate = []
		self._found = False
		self._lock = threading.Condition(threading.Lock())
		return
	
	## Lyrics receive handler.
	def _receive_lyrics(self, raw):
		self._lock.acquire()
		log.debug('enter')
		if not self._found:
			l = LyricsInfo(raw)
			d = distance(self._songinfo, l)
			self._candidate.append([d, l])
			self._found = d == 0
			if self._found:
				self._candidate.sort(candidate_cmp)
				self._callback(self._songinfo, self._candidate)
		log.debug('leave')
		self._lock.release()
		return self._found
	
	## Retrieve lyrics.
	def run(self):
		log.debug('enter')
		threads = []
		token = clean_token(self._songinfo.ar)
		encoding = detect(token)['encoding']
		artist = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
		token = clean_token(self._songinfo.ti)
		encoding = detect(token)['encoding']
		title = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
		for key in self._engine:
			engine = engine_map[key](artist, title, self._receive_lyrics)
			threads.append(engine)
			engine.start()
		for t in threads:
			t.join()
		if not self._found:
			self._candidate.sort(candidate_cmp)
			self._callback(self._songinfo, self._candidate)
		log.debug('leave')
		return
