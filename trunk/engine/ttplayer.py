#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#
#       
#       Copyright 2009 wonder <gogo.wonder@gmail.com>
#       
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
#  千千歌词下载引擎。

import rb, urllib, re, logging, random
from xml.dom.minidom import parseString
from ..utils import clean_token
from lrcbase import LRCBase
log = logging.getLogger('RBLyrics')

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

## 千千歌词下载引擎。
class TTPlayer(LRCBase):
	
	## 构造函数。
	#  @param songinfo 歌曲信息。
	#  @param auto 是否自动匹配歌词。
	#  @param max 最大尝试次数。
	def __init__(self, songinfo, auto, max = 5):
		LRCBase.__init__(self, songinfo, auto, max)
		return
	
	## 搜索页响应函数。
	#  @param xml 得到的响应文本。
	#  @param callback 线程回调函数。
	def _on_meta_arrive(self, xml, callback):
		try:
			elements = parseString(xml).getElementsByTagName('lrc')
		except Exception, e:
			log.warn(e)
			callback(self.__class__.__name__, self._candidate)
		else:
			for element in elements:
				artist = element.getAttribute('artist')
				title = element.getAttribute('title')
				id = int(element.getAttribute('id'))
				url = 'http://lrcct2.ttplayer.com/dll/lyricsvr.dll?dl?Id=%d&Code=%d&uid=01&mac=%012x' %(id,ttpClient.CodeFunc(id,(artist+title).encode('UTF-8', 'ignore')), random.randint(0,0xFFFFFFFFFFFF))
				self._job.append(url)
				if len(self._job) >= self._max:
					break
			log.debug('%d jobs found' % len(self._job))
			self._get_next_lyrics(callback)
		return
	
	## 开始搜索。
	#  @param callback 线程回调函数。
	def search(self, callback):
		artist = clean_token(self._songinfo.ar)
		if artist == clean_token('Unknown'):
			artist = ''
		title = clean_token(self._songinfo.ti)
		artist_token = ttpClient.EncodeArtTit(artist.replace(' ','').lower())
		title_token = ttpClient.EncodeArtTit(title.replace(' ','').lower())
		url='http://lrcct2.ttplayer.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' %(artist_token, title_token)
		log.debug('search url <%s>' % url)
		rb.Loader().get_url(url, self._on_meta_arrive, callback)
		return
