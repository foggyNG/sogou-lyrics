#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import re, cookielib, urllib2, logging, chardet
from Song import init_song_result
from utils import clean_token

class EngineSogou:
	
	def __init__(self, timeout = 3, max = 5):
		logging.debug('enter')
		self.__timeout = timeout
		self.__max = max
		logging.debug('leave')
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
			logging.debug('search page <%s>' % url)
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			cache = opener.open(url, None, self.__timeout).readlines()
			urllist = []
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
					logging.debug('lyrics page <%s>' % url)
					cache = opener.open(url, None, self.__timeout).readlines()
					for line in cache:
						encoding = chardet.detect(line)['encoding']
						try:
							line = line.decode(encoding)
						except:
							continue
						# grab lyrics file url, try all of them
						m = re.search('downlrc\.jsp\?[^\"]*', line)
						if m != None:
							urllist.append('http://mp3.sogou.com/%s' % m.group(0))
					break
			logging.info('%d candidates found' % min(len(urllist), self.__max))
			for url in urllist:
				try:
					cache = opener.open(url, None, self.__timeout).read()
					encoding = chardet.detect(cache)['encoding']
					ins = init_song_result(song, cache.decode(encoding).encode('utf-8'))
					logging.info('[score = %d] <%s>' % (ins.edit_distance_, url))
					retval.append(ins)
					if ins.edit_distance_ == 0 or len(retval) >= self.__max:
						break
				except Exception as e:
					logging.error(e)
		except Exception as e:
			logging.error(e)
		logging.debug('leave')
		return retval
