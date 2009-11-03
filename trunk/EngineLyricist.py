#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib2, chardet, re
from utils import log
from xml.dom.minidom import parseString
from Song import init_song_result
from utils import clean_token

class EngineLyricist:
	
	def __init__(self, timeout = 3, max = 5):
		log.debug('enter')
		self.__timeout = timeout
		self.__max = max
		log.debug('leave')
		return
	
	def clean_token(self, token):
		return re.sub('[\ \t~`!@#$%\^&*\(\)-_+=|\\\{\}\[\]:\";\'<>\?,\./]', '', token)
		
	def search(self, song):
		log.debug('enter')
		retval = []
		token = self.clean_token(clean_token(song.songinfo_['ti']))
		encoding = chardet.detect(token)['encoding']
		title_token = urllib2.quote(token.decode(encoding, 'ignore').encode('UTF-8', 'ignore'))
		token = self.clean_token(clean_token(song.songinfo_['ar']))
		encoding = chardet.detect(token)['encoding']
		artist_token = urllib2.quote(token.decode(encoding, 'ignore').encode('UTF-8', 'ignore'))
		url = 'http://www.winampcn.com/lrceng/get.aspx?song=%s&artist=%s&lsong=%s&prec=1&Datetime=20060601' % (title_token, artist_token, title_token)
		log.debug('search url <%s>' % url)
		try:
			xml = urllib2.urlopen(url, None, self.__timeout).read()
		except Exception as e:
			log.error(e)
		else:
			elements = parseString(xml).getElementsByTagName('LyricUrl')
			for element in elements:
				url = element.firstChild.data
				try:
					cache = urllib2.urlopen(url, None, self.__timeout).read()
				except Exception as e:
					log.error(e)
				else:
					encoding = chardet.detect(cache)['encoding']
					cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
					ins = init_song_result(song, cache)
					log.info('[score = %d] <%s>' % (ins.edit_distance_, url))
					retval.append(ins)
					if ins.edit_distance_ == 0 or len(retval) >= self.__max:
						break
			log.info('%d candidates found' % len(retval))
		log.debug('leave')
		return retval
