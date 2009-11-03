#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import threading
from utils import log
from EngineSogou import EngineSogou
from EngineTT import EngineTT
from EngineMini import EngineMini
from EngineLyricist import EngineLyricist
from Song import song_cmp
from multiprocessing import Pool

engine_map = {
	'ttplayer' : EngineTT,
	'sogou' : EngineSogou,
	'minilyrics': EngineMini,
	'lyricist': EngineLyricist
}

def handler(engine, args):
	return engine.search(args)
	
class Engine:
	
	def __init__(self, engine, song):
		log.debug('enter')
		self.__engine = engine
		self.__song = song
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
			pool.apply_async(handler, [engine(), self.__song], {}, self.__receive_lyrics)
		pool.close()
		pool.join()
		self.__candidate.sort(song_cmp)
		log.debug('leave (%d)' % len(self.__candidate))
		return self.__candidate
