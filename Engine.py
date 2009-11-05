#!/usr/bin/env python
#-*- coding: UTF-8 -*-

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

import threading
from multiprocessing import Pool

from utils import log
from EngineSogou import EngineSogou
from EngineTT import EngineTT
from EngineMini import EngineMini
from EngineLyricist import EngineLyricist

## Lyrics search engine map.
engine_map = {
	'ttplayer' : EngineTT,
	'sogou' : EngineSogou,
	'minilyrics': EngineMini,
	'lyricist': EngineLyricist
}

## Search engine handler for multiprocessing.
def handler(engine, args):
	return engine.search(args)

## Lyrics candidate comparison handler.
def candidate_cmp(x, y):
	return x[0] - y[0]

## Lyrics search engine manager.
class Engine:
	
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
	def __init__(self, engine, songinfo):
		log.debug('enter')
		self._engine = engine
		self._songinfo = songinfo
		self._candidate = []
		self._lock = threading.Condition(threading.Lock())
		log.debug('leave')
		return
	
	## Lyrics receive handler.
	#  @param lyrics Lyrics received.
	def _receive_lyrics(self, lyrics):
		self._lock.acquire()
		self._candidate += lyrics
		self._lock.release()
		return
		
	## Retrieve lyrics.
	#  @return Lyrics candidate list.
	def get_lyrics(self):
		log.debug('enter')
		pool = Pool(len(self._engine))
		for key in self._engine:
			engine = engine_map[key]
			pool.apply_async(handler, [engine(), self._songinfo], {}, self._receive_lyrics)
		pool.close()
		pool.join()
		self._candidate.sort(candidate_cmp)
		log.debug('leave (%d)' % len(self._candidate))
		return self._candidate
