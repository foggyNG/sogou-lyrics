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

## @package RBLyrics.engine.lyricist
#  乐辞歌词下载引擎。

import rb, urllib, re, logging
from xml.dom.minidom import parseString
from ..utils import clean_token
from lrcbase import LRCBase
log = logging.getLogger('RBLyrics')

## 乐辞歌词下载引擎。
class Lyricist(LRCBase):
	
	## 构造函数。
	#  @param songinfo 歌曲信息。
	#  @param auto 是否自动匹配歌词。
	#  @param max 最大尝试次数。
	def __init__(self, songinfo, auto, max = 5):
		LRCBase.__init__(self, songinfo, auto, max)
		return
	
	## 清除特殊字符。
	#  @param token 输入字符串。
	#  @return 清除后的字符串。
	def _clean_token(self, token):
		return re.sub('[\ \t~`!@#$%\^&*\(\)-_+=|\\\{\}\[\]:\";\'<>\?,\./]', '', token)
	
	## 搜索页响应函数。
	#  @param xml 得到的响应文本。
	#  @param callback 线程回调函数。
	def _on_meta_arrive(self, xml, callback):
		try:
			elements = parseString(xml).getElementsByTagName('LyricUrl')
		except Exception, e:
			log.warn(e)
			callback(self.__class__.__name__, self._candidate)
		else:
			for element in elements:
				self._job.append(element.firstChild.data)
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
		artist_token = urllib.quote(self._clean_token(artist))
		title_token = urllib.quote(self._clean_token(title))
		url = 'http://www.winampcn.com/lrceng/get.aspx?song=%s&artist=%s&lsong=%s&prec=1&Datetime=20060601' % (title_token, artist_token, title_token)
		log.debug('search url <%s>' % url)
		rb.Loader().get_url(url, self._on_meta_arrive, callback)
		return
