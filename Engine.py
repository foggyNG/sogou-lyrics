#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import logging, threading
from EngineSogou import EngineSogou
from EngineTT import EngineTT
from EngineMini import EngineMini
from Song import song_cmp
from multiprocessing import Pool

engine_map = {
	'ttplayer' : EngineTT,
	'sogou' : EngineSogou,
	'minilyrics': EngineMini
}

def handler(engine, args):
	return engine.search(args)
	
class Engine:
	
	def __init__(self, engine, song):
		self.__engine = engine
		self.__song = song
		self.__candidate = []
		self.__lock = threading.Condition(threading.Lock())
		return
	
	def __receive_lyrics(self, lyrics):
		self.__lock.acquire()
		self.__candidate += lyrics
		self.__lock.release()
		return
		
	def get_lyrics(self):
		logging.debug('enter')
		pool = Pool(len(self.__engine))
		for key in self.__engine:
			engine = engine_map[key]
			pool.apply_async(handler, [engine(), self.__song], {}, self.__receive_lyrics)
		pool.close()
		pool.join()
		self.__candidate.sort(song_cmp)
		logging.debug('leave')
		return self.__candidate
