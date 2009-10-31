#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, logging, chardet
from xml.dom.minidom import parse, parseString
from hashlib import md5
from Song import init_song_result
from utils import clean_token

class EngineMini:
	
	def __init__(self, timeout = 3, max = 5):
		self.__timeout = timeout
		self.__max = max
		return
		
	def search(self, song):
		logging.debug('enter')
		retval = []
		token = clean_token(song.songinfo_['ti'])
		encoding = chardet.detect(token)['encoding']
		title_token = token.decode(encoding).encode('utf-8')
		token = clean_token(song.songinfo_['ar'])
		encoding = chardet.detect(token)['encoding']
		artist_token = token.decode(encoding).encode('utf-8')		
		xml = "<?xml version=\"1.0\" encoding='utf-8'?>\r\n"
		xml += "<search filetype=\"lyrics\" artist=\"%s\" title=\"%s\" " % (artist_token, title_token)
		xml += "ClientCharEncoding=\"utf-8\"/>\r\n"
		m = md5()
		m.update(xml + 'Mlv1clt4.0')
		request = '\x02\x00\x04\x00\x00\x00%s%s' % (m.digest(), xml)
		url = 'http://www.viewlyrics.com:1212/searchlyrics.htm'
		try:
			xml = urllib2.urlopen(url, request, self.__timeout).read()
			dom = parseString(xml)
			elements = dom.getElementsByTagName('fileinfo')
			logging.info('%d candidates found' % min(len(elements), self.__max))
			for element in elements:
				try:
					url = element.getAttribute('link')
					cache = urllib2.urlopen(url, None, self.__timeout).read()
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
