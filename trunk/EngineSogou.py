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
		token = clean_token(song.songinfo_['ti'])
		encoding = chardet.detect(token)['encoding']
		title_encode = urllib2.quote(token.decode(encoding, 'ignore').encode('gbk', 'ignore'))
		token = clean_token(song.songinfo_['ar'])
		encoding = chardet.detect(token)['encoding']
		artist_encode = urllib2.quote(token.decode(encoding, 'ignore').encode('gbk', 'ignore'))
		url = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_encode, title_encode)
		logging.debug('search page <%s>' % url)
		try:
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			cache = opener.open(url, None, self.__timeout).read()
			encoding = chardet.detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').splitlines()
		except Exception as e:
			logging.error(e)
		else:
			for line in cache:
				# grab lyrics search page, only use the first
				m = re.search('geci\.so\?[^\"]*', line)
				if m != None:
					url = 'http://mp3.sogou.com/%s' % m.group(0)
					logging.debug('lyrics page <%s>' % url)
					try:
						cache = opener.open(url, None, self.__timeout).read()
						encoding = chardet.detect(cache)['encoding']
						cache = cache.decode(encoding, 'ignore').splitlines()
					except Exception as e:
						logging.error(e)
					else:
						# grab lyrics file url, try all of them
						for line in cache:
							m = re.search('downlrc\.jsp\?[^\"]*', line)
							if m != None:
								url = 'http://mp3.sogou.com/%s' % m.group(0)
								try:
									cache = opener.open(url, None, self.__timeout).read()
								except Exception as e:
									logging.error(e)
								else:
									encoding = chardet.detect(cache)['encoding']
									cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
									ins = init_song_result(song, cache)
									logging.info('[score = %d] <%s>' % (ins.edit_distance_, url))
									retval.append(ins)
									if ins.edit_distance_ == 0 or len(retval) >= self.__max:
										break
						logging.info('%d candidates found' % len(retval))
					break
			else:
				logging.info('0 candidates found')
		logging.debug('leave')
		return retval
