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

import threading, time
from chardet import detect

from sogou import Sogou
from ttplayer import TTPlayer
from minilyrics import Minilyrics
from lyricist import Lyricist
from utils import log, clean_token, distance, LyricsInfo, save_lyrics

## Lyrics search engine map.
engine_map = {
	#'ttplayer' : TTPlayer,
	'sogou' : Sogou,
	'minilyrics': Minilyrics,
	'lyricist': Lyricist
}

## Lyrics candidate comparison handler.
def candidate_cmp(x, y):
	return x[0] - y[0]

## Lyrics search engine manager.
class Engine(threading.Thread):
	
	## @var _engine
	#  Lyrics engine keys.
	
	## @var _songinfo
	#  Song information.
	
	## @var _candidate
	#  Lyrics candidates.
	
	## @var _lock
	#  Thread lock for appending _candidate list.
	
	## The constructor.
	#  @param engine Engine list.
	#  @param songinfo Song information.
	def __init__(self, prefs, songinfo, callback):
		threading.Thread.__init__(self)
		log.debug('enter')
		self._prefs = prefs
		self._songinfo = songinfo
		self._callback = callback
		self._candidate = []
		self._lock = threading.Condition(threading.Lock())
		log.debug('leave')
		return
	
	## Lyrics receive handler.
	#  @param engine Lyrics search engine.
	#  @param artist Song artist.
	#  @param title Song title.
	def _receive_lyrics(self, candidate):
		self._lock.acquire()
		for raw in candidate():
			self._candidate.append(raw)
		self._lock.release()
		return
	
	## Retrieve lyrics.
	#  @return Lyrics candidate list.
	def run(self):
		log.debug('enter')
		threads = []
		for key in self._prefs.get_engine():
			engine = engine_map[key]()
			threads.append(engine)
		for t in threads:
			t.search(self._songinfo)
		finished = False
		found = False
		while not finished:
			time.sleep(0.5)
			finished = True
			for t in threads:
				if t.is_alive():
					finished = False
					if found:
						t.stop()
				else:
					threads.remove(t)
					for c in t.candidate():
						if c[0] == 0:
							found = True
						self._candidate.append(c)
		self._candidate.sort(candidate_cmp)
		self._callback(self._songinfo, self._candidate)
		log.debug('leave')
		return