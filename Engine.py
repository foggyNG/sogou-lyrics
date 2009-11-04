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

engine_map = {
	'ttplayer' : EngineTT,
	'sogou' : EngineSogou,
	'minilyrics': EngineMini,
	'lyricist': EngineLyricist
}

def handler(engine, args):
	return engine.search(args)

def candidate_cmp(x, y):
	return x[0] - y[0]
	
class Engine:
	
	def __init__(self, engine, songinfo):
		log.debug('enter')
		self.__engine = engine
		self.__songinfo = songinfo
		self.__candidate = []
		self.__lock = threading.Condition(threading.Lock())
		log.debug('leave')
		return
	
	def __receive_lyrics(self, lyrics):
		self.__lock.acquire()
		self.__candidate += lyrics
		self.__lock.release()
		return
		
	def get_lyrics(self):
		log.debug('enter')
		pool = Pool(len(self.__engine))
		for key in self.__engine:
			engine = engine_map[key]
			pool.apply_async(handler, [engine(), self.__songinfo], {}, self.__receive_lyrics)
		pool.close()
		pool.join()
		self.__candidate.sort(candidate_cmp)
		log.debug('leave (%d)' % len(self.__candidate))
		return self.__candidate
