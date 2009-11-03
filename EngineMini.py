#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib2, chardet
from utils import log
from xml.dom.minidom import parseString
from hashlib import md5
from Song import init_song_result
from utils import clean_token

class EngineMini:
	
	def __init__(self, timeout = 3, max = 5):
		log.debug('enter')
		self.__timeout = timeout
		self.__max = max
		log.debug('leave')
		return
		
	def search(self, song):
		log.debug('enter')
		retval = []
		token = clean_token(song.songinfo_['ti'])
		encoding = chardet.detect(token)['encoding']
		title_token = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
		token = clean_token(song.songinfo_['ar'])
		encoding = chardet.detect(token)['encoding']
		artist_token = token.decode(encoding, 'ignore').encode('UTF-8', 'ignore')		
		xml = "<?xml version=\"1.0\" encoding='utf-8'?>\r\n"
		xml += "<search filetype=\"lyrics\" artist=\"%s\" title=\"%s\" " % (artist_token, title_token)
		xml += "ClientCharEncoding=\"utf-8\"/>\r\n"
		m = md5()
		m.update(xml + 'Mlv1clt4.0')
		request = '\x02\x00\x04\x00\x00\x00%s%s' % (m.digest(), xml)
		url = 'http://www.viewlyrics.com:1212/searchlyrics.htm'
		try:
			xml = urllib2.urlopen(url, request, self.__timeout).read()
		except Exception as e:
			log.error(e)
		else:
			elements = parseString(xml).getElementsByTagName('fileinfo')
			for element in elements:
				url = element.getAttribute('link')
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
