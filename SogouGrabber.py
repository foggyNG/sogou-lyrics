import re, ClientCookie, urllib2
from utils import *

class SogouGrabber:
	
	def __init__(self, artist, title, lrc_path):
		self.artist = artist
		self.title = title
		self.lrc_path = lrc_path
		
	def search(self):
		print 'enter'
		retval = []
		# grab song search page
		title_encode = urllib2.quote(detect_charset(clean_token(self.title)).encode('gbk'))
		artist_encode = urllib2.quote(detect_charset(clean_token(self.artist)).encode('gbk'))
		uri = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_encode, title_encode)
		print 'search page <%s>' % uri
		cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
		for line in cache:
			# grab lyrics search page, only use the first
			m = re.search('geci\.so\?[^\"]*', line.decode('gbk'))
			if not m is None:
				uri = 'http://mp3.sogou.com/%s' % m.group(0)
				print 'lyrics page <%s>' % uri
				cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
				for line in cache:
					# grab lyrics file uri, try all of them
					m = re.search('downlrc\.jsp\?[^\"]*', line.decode('gbk'))
					if not m is None:				
						uri = 'http://mp3.sogou.com/%s' % m.group(0)
						print 'lyrics file <%s>' % uri
						cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
						lrc = []
						for line in cache:
							lrc.append(line.decode('gbk').encode('utf-8'))
						retval.append(lrc)
				break
		print 'leave'
		return retval
