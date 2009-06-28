import re
from utils import *
from Preference import Preference
from SogouGrabber import SogouGrabber
from ttPlayerGrabber import ttPlayerGrabber
from threading import Thread

grabber_map = {
	'ttPlayer' : ttPlayerGrabber,
	'Sogou' : SogouGrabber
}
class Grabber(Thread):
	
	def __init__(self, engines, artist, title, lrc_path):
		self.engines = engines
		self.artist = artist
		self.title = title
		self.lrc_path = lrc_path
		Thread.__init__(self)
		return
	
	def run(self):
		print 'enter'
		found = False
		candidate = []
		for key in self.engines:
			try:
				engine = grabber_map[key]
				received = engine(self.artist, self.title, self.lrc_path).search()
				for lrc in received:
					lrc_content = parse_lyrics(lrc)
					if verify_lyrics(lrc_content, self.artist, self.title):
						found = True
						open(self.lrc_path, 'w').writelines(lrc)
						break
					else:
						artist = ''
						title = ''
						if lrc_content.has_key('ar'):
							artist = lrc_content['ar']
						if lrc_content.has_key('ti'):
							title = lrc_content['ti']
						candidate.append([artist, title, lrc])
				if found:
					break
			except KeyError:
				pass
		if not found:
			print '%d candidates found' % len(candidate)
			for c in candidate:
				print 'candidate: %s - %s' % (c[0], c[1])
		print 'leave'
		return

