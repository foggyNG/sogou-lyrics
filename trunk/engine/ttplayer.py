#!/usr/bin/env python
#-*- coding: UTF-8 -*-

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

## @package RBLyrics.engine.ttplayer
#  TTPlayer search engine.

import random, urllib2, sys
from xml.dom.minidom import parseString

from RBLyrics.chardet import detect
from RBLyrics.utils import log, clean_token, distance, LyricsInfo, SongInfo

## TTPlayer lyrics server crack functionality.
#
#  Provide ttplayer specific function, such as encoding artist and title,
#  generate a Id code for server authorizition.
#  (see http://ttplyrics.googlecode.com/svn/trunk/crack) 
class ttpClient:

	## Generate a Id Code.
	#  These code may be ugly coz it is translated
	#  from C code which is translated from asm code
	#  grabed by ollydbg from ttp_lrcs.dll.
	#  (see http://ttplyrics.googlecode.com/svn/trunk/crack)
    @staticmethod
    def CodeFunc(Id, data):
	length = len(data)

	tmp2=0
	tmp3=0

	tmp1 = (Id & 0x0000FF00) >> 8							#右移8位后为x0000015F

	    #tmp1 0x0000005F
	if ( (Id & 0x00FF0000) == 0 ):
	    tmp3 = 0x000000FF & ~tmp1							#CL 0x000000E7
	else:
	    tmp3 = 0x000000FF & ((Id & 0x00FF0000) >> 16)                               #右移16后为x00000001

	tmp3 = tmp3 | ((0x000000FF & Id) << 8)                                          #tmp3 0x00001801
	tmp3 = tmp3 << 8                                                                #tmp3 0x00180100
	tmp3 = tmp3 | (0x000000FF & tmp1)                                               #tmp3 0x0018015F
	tmp3 = tmp3 << 8                                                                #tmp3 0x18015F00
	if ( (Id & 0xFF000000) == 0 ) :
	    tmp3 = tmp3 | (0x000000FF & (~Id))                                          #tmp3 0x18015FE7
	else :
	    tmp3 = tmp3 | (0x000000FF & (Id >> 24))                                     #右移24位后为0x00000000

	#tmp3	18015FE7
        
	i=length-1
	while(i >= 0):
	    char = ord(data[i])
	    if char >= 0x80:
		char = char - 0x100
	    tmp1 = (char + tmp2) & 0x00000000FFFFFFFF
	    tmp2 = (tmp2 << (i%2 + 4)) & 0x00000000FFFFFFFF
	    tmp2 = (tmp1 + tmp2) & 0x00000000FFFFFFFF
	    #tmp2 = (ord(data[i])) + tmp2 + ((tmp2 << (i%2 + 4)) & 0x00000000FFFFFFFF)
	    i -= 1

	#tmp2 88203cc2
	i=0
	tmp1=0
	while(i<=length-1):
	    char = ord(data[i])
	    if char >= 128:
		char = char - 256
	    tmp7 = (char + tmp1) & 0x00000000FFFFFFFF
	    tmp1 = (tmp1 << (i%2 + 3)) & 0x00000000FFFFFFFF
	    tmp1 = (tmp1 + tmp7) & 0x00000000FFFFFFFF
	    #tmp1 = (ord(data[i])) + tmp1 + ((tmp1 << (i%2 + 3)) & 0x00000000FFFFFFFF)
	    i += 1

	#EBX 5CC0B3BA

	#EDX = EBX | Id
	#EBX = EBX | tmp3
	tmp1 = (((((tmp2 ^ tmp3) & 0x00000000FFFFFFFF) + (tmp1 | Id)) & 0x00000000FFFFFFFF) * (tmp1 | tmp3)) & 0x00000000FFFFFFFF
	tmp1 = (tmp1 * (tmp2 ^ Id)) & 0x00000000FFFFFFFF

	if tmp1 > 0x80000000:
	    tmp1 = tmp1 - 0x100000000
	return tmp1
    
    @staticmethod
    def EncodeArtTit(str):
	rtn = ''
	str = str.encode('UTF-16', 'ignore')[2:]
	for i in range(len(str)):
	    rtn += '%02x' % ord(str[i])

	return rtn

## QianQian player engine.
#
#  Retrieve lyrics from www.ttplayer.com.
class TTPlayer:

	## @var _timeout
	#  HTTP request timeout.
	
	## @var _max
	#  Max number of lyrics expected.
	
	## The constructor.
	#  @param timeout HTTP request timeout.
	#  @param max Max number of lyrics expected.
	def __init__(self, timeout = 3, max = 5):
		log.debug('enter')
		self._timeout = timeout
		self._max = max
		log.debug('leave')
		return
	
	## Retrieve lyrics.
	#  @param songinfo Song information.
	#  @return Lyrics candidate list.
	def search(self, songinfo):
		log.debug('enter')
		retval = []
		token = clean_token(songinfo.get('ti'))
		encoding = detect(token)['encoding']
		title_token = ttpClient.EncodeArtTit(token.decode(encoding, 'ignore').encode('UTF-8', 'ignore').replace(' ','').lower())
		token = clean_token(songinfo.get('ar'))
		encoding = detect(token)['encoding']
		artist_token = ttpClient.EncodeArtTit(token.decode(encoding, 'ignore').encode('UTF-8', 'ignore').replace(' ','').lower())
		url='http://lrcct2.ttplayer.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' %(artist_token, title_token)
		log.debug('search url <%s>' % url)
		try:
			cache = urllib2.urlopen(url, None, self._timeout).read()
		except Exception as e:
			log.error(e)
		else:
			elements = parseString(cache).getElementsByTagName('lrc')
			for element in elements:
				artist = element.getAttribute('artist')
				title = element.getAttribute('title')
				id = int(element.getAttribute('id'))
				url = 'http://lrcct2.ttplayer.com/dll/lyricsvr.dll?dl?Id=%d&Code=%d&uid=01&mac=%012x' %(id,ttpClient.CodeFunc(id,(artist+title).encode('UTF-8', 'ignore')), random.randint(0,0xFFFFFFFFFFFF))
				try:
					cache = urllib2.urlopen(url, None, self._timeout).read()
				except Exception as e:
					log.error(e)
				else:
					encoding = detect(cache)['encoding']
					cache = cache.decode(encoding, 'ignore').encode('utf-8', 'ignore')
					lyrics = LyricsInfo(cache)
					dist = distance(songinfo, lyrics)
					log.info('[score = %d] <%s>' % (dist, url))
					retval.append([dist, lyrics])
					if dist == 0 or len(retval) >= self._max:
						break
			log.info('%d candidates found' % len(retval))
		log.debug('leave')
		return retval
		
