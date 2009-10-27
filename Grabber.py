#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, re, logging
from utils import *
from Preference import Preference
from SogouGrabber import SogouGrabber
from ttPlayerGrabber import ttPlayerGrabber
from MiniLyrics import MiniLyrics
from threading import Thread
from LyricsChooser import LyricsChooser
from gtk import gdk

grabber_map = {
	'ttPlayer' : ttPlayerGrabber,
	'Sogou' : SogouGrabber,
	'Mini': MiniLyrics
}
class Grabber:
	
	def __init__(self, engines, lrcinfo, callback):
		self.engines = engines
		self.lrcinfo = lrcinfo
		self.callback = callback
		return
	
	def run(self):
		logging.debug('enter')
		found = False
		candidate = []
		for key in self.engines:
			engine = grabber_map[key]
			received = engine().search(self.lrcinfo)
			candidate += received
			received.sort()
			if len(received) > 0 and received[0][0] == 0:
				break
		candidate.sort()
		self.callback(candidate, self.lrcinfo)
		logging.debug('leave')
		return
	
	def get_lyrics(self):
		self.run()
		return
