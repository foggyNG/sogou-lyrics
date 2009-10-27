#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import re, ClientCookie, urllib2, logging
from utils import *
import chardet

class SogouGrabber:
	
	def __init__(self):
		return
		
	def search(self, lrcinfo):
		logging.debug('enter')
		retval = []
		try:
			# grab song search page
			title_encode = urllib2.quote(detect_charset(clean_token(lrcinfo['ti'])).encode('gbk'))
			artist_encode = urllib2.quote(detect_charset(clean_token(lrcinfo['ar'])).encode('gbk'))
			uri = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_encode, title_encode)
			logging.info('search page <%s>' % uri)
			cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
			encoding = chardet.detect(cache[0])['encoding']
			for line in cache:
				# grab lyrics search page, only use the first
				try:
					m = re.search('geci\.so\?[^\"]*', line.decode(encoding))
				except:
					continue
				if not m is None:
					uri = 'http://mp3.sogou.com/%s' % m.group(0)
					logging.info('lyrics page <%s>' % uri)
					cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
					encoding2 = chardet.detect(cache[0])['encoding']
					for line in cache:
						# grab lyrics file uri, try all of them
						try:
							m = re.search('downlrc\.jsp\?[^\"]*', line.decode(encoding2))
						except:
							continue
						if not m is None:
							uri = 'http://mp3.sogou.com/%s' % m.group(0)
							logging.info('lyrics file <%s>' % uri)
							cache = ClientCookie.urlopen(ClientCookie.Request(uri)).read()
							encoding3 = chardet.detect(cache)['encoding']
							ins = gen_lrc_instance(cache.decode(encoding3).encode('utf-8'), lrcinfo)
							retval.append(ins)
							if ins[0] == 0:
								break
					break
		except Exception as e:
			logging.error(e)
		logging.debug('leave')
		return retval
