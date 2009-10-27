#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, logging
from xml.dom.minidom import parse, parseString
from hashlib import md5
from utils import gen_lrc_instance
import chardet

class MiniLyrics:
	
	def __init__(self):
		return
		
	def search(self, lrcinfo):
		logging.debug('enter')
		retval = []
		title  = lrcinfo['ti' ]
		artist = lrcinfo['ar']
		
		xml = "<?xml version=\"1.0\" encoding='utf-8'?>\r\n"
		xml += "<search filetype=\"lyrics\" artist=\"%s\" title=\"%s\" " % (artist.encode('utf-8'), title.encode('utf-8'))
		xml += "ClientCharEncoding=\"utf-8\"/>\r\n"
		m = md5()
		m.update(xml + "Mlv1clt4.0")
		request = "\x02\x00\x04\x00\x00\x00%s%s" % (m.digest(), xml)
		del m,xml
	
		url="http://www.viewlyrics.com:1212/searchlyrics.htm"
		#print request
		req = urllib2.Request(url, request)
		req.add_header("User-Agent", "MiniLyrics")
		
		try:
			response = urllib2.urlopen(url, request)
			xml = response.read()
			response.close()

			dom = parseString(xml)

			elements = dom.getElementsByTagName('fileinfo')
			
			for element in elements:
				try:
					url = element.getAttribute('link')
					logging.info('lyrics file <%s>' % url)
					cache = urllib2.urlopen(url).read()
					encoding = chardet.detect(cache)['encoding']
					ins = gen_lrc_instance(cache.decode(encoding).encode('utf-8'), lrcinfo)
					retval.append(ins)
					if ins[0] == 0:
						break
				except IOError:
					pass
		except Exception as e:
			logging.error(e)
		logging.debug('leave')
		return retval
