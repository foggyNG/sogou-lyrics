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

## @package RBLyrics.engine
#  Lyrics search engine.

import threading
from multiprocessing import Pool

from RBLyrics.chardet import detect
from RBLyrics.engine.sogou import Sogou
from RBLyrics.engine.ttplayer import TTPlayer
from RBLyrics.engine.minilyrics import Minilyrics
from RBLyrics.engine.lyricist import Lyricist
from RBLyrics.utils import log, clean_token, distance, LyricsInfo

## Lyrics search engine map.
engine_map = {
	'ttplayer' : TTPlayer,
	'sogou' : Sogou,
	'minilyrics': Minilyrics,
	'lyricist': Lyricist
}

## Search engine handler for multiprocessing.
def handler(engine, artist, title):
	return engine.search(artist, title)

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
		for raw in lyrics:
			l = LyricsInfo(raw)
			d = distance(self._songinfo, l)
			self._candidate.append([d, l])
		self._lock.release()
		return
		
	## Retrieve lyrics.
	#  @return Lyrics candidate list.
	def get_lyrics(self):
		log.debug('enter')
		pool = Pool(len(self._engine))
		for key in self._engine:
			engine = engine_map[key]
			token = clean_token(self._songinfo.get('ar'))
			encoding = detect(token)['encoding']
			artist = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
			token = clean_token(self._songinfo.get('ti'))
			encoding = detect(token)['encoding']
			title = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
			pool.apply_async(handler, [engine(), artist, title], {}, self._receive_lyrics)
		pool.close()
		pool.join()
		self._candidate.sort(candidate_cmp)
		log.debug('leave (%d)' % len(self._candidate))
		return self._candidate
