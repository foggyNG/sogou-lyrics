#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, re, logging
from EngineSogou import EngineSogou
from EngineTT import EngineTT
from EngineMini import EngineMini
from LyricsChooser import LyricsChooser
from Song import song_cmp

engine_map = {
	'ttPlayer' : EngineTT,
	'Sogou' : EngineSogou,
	'Mini': EngineMini
}
class Engine:
	
	def __init__(self, engine, song, callback):
		self.engine_ = engine
		self.song_ = song
		self.callback_ = callback
		return
	
	def run(self):
		logging.debug('enter')
		found = False
		candidate = []
		for key in self.engine_:
			engine = engine_map[key]
			received = engine().search(self.song_)
			candidate += received
			received.sort(song_cmp)
			if len(received) > 0 and received[0].edit_distance_ == 0:
				break
		candidate.sort(song_cmp)
		self.callback_(candidate, self.song_)
		logging.debug('leave')
		return
	
	def get_lyrics(self):
		self.run()
		return
