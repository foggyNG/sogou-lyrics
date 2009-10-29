#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, re, logging
from EngineSogou import EngineSogou
from EngineTT import EngineTT
from EngineMini import EngineMini
from LyricsChooser import LyricsChooser
from Song import song_cmp
from multiprocessing import Pool
import threading

engine_map = {
	'ttPlayer' : EngineTT,
	'Sogou' : EngineSogou,
	'Mini': EngineMini
}

def handler(engine, args):
	return engine.search(args)
	
class Engine:
	
	def __init__(self, engine, song):
		self.engine_ = engine
		self.song_ = song
		self.candidate_ = []
		self.__lock = threading.Condition(threading.Lock())
		return
	
	def receive_lyrics(self, lyrics):
		self.__lock.acquire()
		self.candidate_ += lyrics
		self.__lock.release()
		return
		
	def get_lyrics(self):
		logging.debug('enter')
		found = False
		pool = Pool(len(self.engine_))
		for key in self.engine_:
			engine = engine_map[key]
			pool.apply_async(handler, [engine(), self.song_], {}, self.receive_lyrics)
		pool.close()
		pool.join()
		self.candidate_.sort(song_cmp)
		logging.debug('leave')
		return self.candidate_
