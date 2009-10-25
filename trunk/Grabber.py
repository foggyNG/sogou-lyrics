#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, re, logging
from utils import *
from Preference import Preference
from SogouGrabber import SogouGrabber
from ttPlayerGrabber import ttPlayerGrabber
from threading import Thread
from LyricsChooser import LyricsChooser
from gtk import gdk

grabber_map = {
	'ttPlayer' : ttPlayerGrabber,
	'Sogou' : SogouGrabber
}
class Grabber:
	
	def __init__(self, engines, artist, title, lrc_path, callback):
		self.engines = engines
		self.artist = artist
		self.title = title
		self.lrc_path = lrc_path
		self.callback = callback
		return
	
	def run(self):
		logging.debug('enter')
		found = False
		candidate = []
		for key in self.engines:
			try:
				engine = grabber_map[key]
				received = engine(self.artist, self.title).search()
				for lrc in received:
					lrc_content = parse_lyrics(lrc)
					dist = verify_lyrics(lrc_content, self.artist, self.title)
					artist = ''
					title = ''
					if lrc_content.has_key('ar'):
						artist = lrc_content['ar']
					if lrc_content.has_key('ti'):
						title = lrc_content['ti']
					candidate.append([dist, artist, title, lrc])
					if dist == 0:
						found = True
						break
				if found:
					break
			except KeyError:
				pass
		candidate.sort()
		self.callback(candidate, self.artist, self.title, self.lrc_path)
		logging.debug('leave')
		return
	
	def get_lyrics(self):
		self.run()
		return
