import re
from utils import *
from Preference import Preference
from SogouGrabber import SogouGrabber
from ttPlayerGrabber import ttPlayerGrabber

grabber_map = {
	'Sogou' : SogouGrabber,
	'ttPlayer' : ttPlayerGrabber
}
class Grabber(object):
	
	def __init__(self, prefs):
		self.prefs = prefs
		return
	
	def grab(self, artist, title, lrc_path):
		for key in self.prefs.get_pref('grabber'):
			try:
				grabber = grabber_map[key]
				grabber(artist, title, lrc_path).start()
			except KeyError:
				pass
		return

