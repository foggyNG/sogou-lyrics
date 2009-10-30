#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import re, ClientCookie, urllib2, logging, chardet, os
from Song import *
from utils import clean_token

class EngineSogou:
	
	def __init__(self, max = 5):
		self.__max = max
		return
		
	def search(self, song):
		logging.debug('enter')
		retval = []
		try:
			# grab song search page
			token = clean_token(song.songinfo_['ti'])
			encoding = chardet.detect(token)['encoding']
			title_encode = urllib2.quote(token.decode(encoding).encode('gbk'))
			token = clean_token(song.songinfo_['ar'])
			encoding = chardet.detect(token)['encoding']
			artist_encode = urllib2.quote(token.decode(encoding).encode('gbk'))
			url = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_encode, title_encode)
			logging.info('search page <%s>' % url)
			cache = ClientCookie.urlopen(ClientCookie.Request(url)).readlines()
			for line in cache:
				encoding = chardet.detect(line)['encoding']
				try:
					line = line.decode(encoding)
				except:
					continue
				# grab lyrics search page, only use the first
				m = re.search('geci\.so\?[^\"]*', line)
				if m != None:
					url = 'http://mp3.sogou.com/%s' % m.group(0)
					logging.info('lyrics page <%s>' % url)
					cache = ClientCookie.urlopen(ClientCookie.Request(url)).readlines()
					for line in cache:
						encoding = chardet.detect(line)['encoding']
						try:
							line = line.decode(encoding)
						except:
							continue
						# grab lyrics file url, try all of them
						m = re.search('downlrc\.jsp\?[^\"]*', line)
						if m != None:
							url = 'http://mp3.sogou.com/%s' % m.group(0)
							cache = ClientCookie.urlopen(ClientCookie.Request(url)).read()
							encoding = chardet.detect(cache)['encoding']
							ins = init_song_result(song, cache.decode(encoding).encode('utf-8'))
							logging.info('[score = %d] <%s>' % (ins.edit_distance_, url))
							retval.append(ins)
							if ins.edit_distance_ == 0 or len(retval) >= self.__max:
								break
					break
		except Exception as e:
			logging.error(e)
		logging.debug('leave')
		return retval
