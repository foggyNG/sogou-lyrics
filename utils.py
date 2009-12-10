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

## @package RBLyrics.utils
#  包含歌曲信息和歌词信息的定义，相关操作和辅助函数。

import re, logging, os, sys, urllib, gettext
from chardet import detect
_ = gettext.gettext
log = logging.getLogger('RBLyrics')

## 用于提取歌曲信息的模板。
TOKEN_STRIP = {'\([^\)]*\)':'', '[\ -]+':' '}
## 歌词存储的结构模式。
LRC_PATH_TEMPLATE = ['%s/%s.lrc', '%s - %s.lrc']
## 歌词标题提取模板。
re_ti = re.compile(r'\[ti:([^\]]*)\]')
## 歌词艺术家提取模板。
re_ar = re.compile(r'\[ar:([^\]]*)\]')
## 歌词时间偏移提取模板。
re_offset = re.compile(r'\[offset:([+-]{0,1}[0-9]+)\]')
## 歌词时间标签提取模板。
re_time = re.compile(r'\[(?P<min>[0-9]{2}):(?P<sec>[0-9]{2})(\.(?P<milli>[0-9]{1,3}))?\]')

## 歌曲信息。
class SongInfo(object):
	
	## 构造函数。
	#  @param artist 艺术家。
	#  @param title 标题。
	def __init__(self, artist, title):
		self._artist = artist
		self._title = title
		return
	
	def __str__(self):
		return '%s - %s' % (self._artist, self._title)
		
	def __eq__(self, other):
		return self._title == other.ti and self._artist == other.ar

	## 艺术家(只读)。
	ar = property(lambda self: self._artist)
	## 标题(只读)。
	ti = property(lambda self: self._title)
	
## 歌词信息。
class LyricsInfo(object):
	
	## 构造函数。
	#  @param raw 歌词原始文本数据。
	def __init__(self, raw):
		self._raw = raw
		self._artist = ''
		self._title = ''
		self._content = {}
		self._parse()
		return
	
	## 由歌词时间标签生成时间，以毫秒为单位。
	#  @param group 时间标签。
	#  @return 毫秒。
	def _make_time(self, group):
		min = int(group.group('min'))
		sec = int(group.group('sec'))
		milli = group.group('milli')
		if milli:
			milli = int(milli) * pow(10, 3-len(milli))
		else:
			milli = 0
		return min*60000 + sec*1000 + milli
		
	## 解析歌词文本。
	def _parse(self):
		lines = self._raw.splitlines()
		cache = {}
		offset = 0
		for line in lines:
			# search for title property
			for ti in re_ti.findall(line):
				self._title = ti
			# search for artist property
			for ar in re_ar.findall(line):
				self._artist = ar
			# search for offset property
			for off in re_offset.findall(line):
				offset = int(off)
			# parse lrc
			timestamp = []
			result = re_time.search(line)
			if result:
				while result:
					timestamp.append(self._make_time(result))
					line = line[result.end():]
					result = re_time.search(line)
				if len(line):
					for t in timestamp:
						cache[t] = line
		tags = cache.keys()
		tags.sort()
		for key in tags:
			second = int(round((key + offset) / 1000.0))
			if second in self._content:
				self._content[second] += ' ' + cache[key]
				self._content[second].replace(os.linesep, ' ')
			else:
				self._content[second] = cache[key]
		if len(self._content) == 0:
			log.warn('empty or invalid lyrics file')
		return
	
	## 艺术家(只读)。
	ar = property(lambda self: self._artist)
	## 标题(只读)。
	ti = property(lambda self: self._title)
	## 原始文本(只读)。
	raw = property(lambda self: self._raw)
	## 解析后的歌词内容(只读)。
	content = property(lambda self: self._content)
	
## 清除信息字段中的冗余部分。
#  @param token 输入信息.
#  @return 清除冗余后的信息.
def clean_token(token):
	result = token.lower()
	for strip in TOKEN_STRIP.keys():
		result = re.sub(strip, TOKEN_STRIP[strip], result)
	result = result.strip()
	return result

## 计算两个序列的编辑距离。
#  @param left 序列A。
#  @param right 序列B。
#  @return 序列A和B的编辑距离。
def edit_distance(left, right):
	m = len(left)
	n = len(right)
	if m == 0 or n == 0:
		return m + n
	dist = []
	for i in range(m+1):
		dist.append(range(n+1))
	for i in range(m+1):
		dist[i][0] = i
	for i in range(n+1):
		dist[0][i] = i
	for i in range(1,m+1):
		for j in range(1,n+1):
			dist[i][j] = min(dist[i-1][j-1] + int(left[i-1] != right[j-1]), dist[i-1][j]+1, dist[i][j-1]+1)
	return dist[m][n]

## 计算歌曲信息和歌词信息间的编辑距离。
#  @param songinfo 歌曲信息。
#  @param lyrics 歌词信息。
#  @return 编辑距离。
def distance(songinfo, lyrics):
	return edit_distance(songinfo.ar.lower(), lyrics.ar.lower()) + edit_distance(songinfo.ti.lower(), lyrics.ti.lower())

## 将歌词写入磁盘。
#  @param root 歌词存储根目录。
#  @param pattern 歌词存储结构。
#  @param songinfo 歌曲信息。
#  @param lyrics 歌词信息。
def save_lyrics(root, pattern, songinfo, lyrics):
	path = os.path.join(root, pattern % (songinfo.ar, songinfo.ti))
	dir = os.path.dirname(path)
	if not os.path.exists(dir):
		os.makedirs(dir)
	open(path, 'w').write(lyrics.raw)
	log.info('save <file://%s>' % urllib.pathname2url(path))
	return

## 从本地载入歌词。
#  @param root 歌词存储根目录。
#  @param songinfo 歌曲信息。
#  @return 歌词信息，未找到时返回None。
def load_lyrics(root, songinfo):
	lyrics = None
	for p in LRC_PATH_TEMPLATE:
		path = os.path.join(root, p % (songinfo.ar, songinfo.ti))
		if os.path.exists(path):
			log.info('load <file://%s>' % urllib.pathname2url(path))
			try:
				cache = open(path, 'r').read()
				guess = {}
				for l in cache.splitlines():
					charset = detect(l)['encoding']
					if charset:
						if guess.has_key(charset):
							guess[charset] += 1
						else:
							guess[charset] = 1
				charset = 'UTF-8'
				threshold = 0
				for c in guess:
					if guess[c] > threshold:
						threshold = guess[c]
						charset = c
				cache = cache.decode(charset, 'ignore').encode('UTF-8', 'ignore')
				lyrics = LyricsInfo(cache)
			except Exception, e:
				log.error(e)
			break
	return lyrics

## 使用系统默认编辑器打开歌词。
#  @param root 歌词存储根目录。
#  @param songinfo 歌曲信息。
#  @return 操作是否成功。
def open_lyrics(root, songinfo):
	ret = False
	for p in LRC_PATH_TEMPLATE:
		path = os.path.join(root, p % (songinfo.ar, songinfo.ti))
		if os.path.exists(path):
			log.info('open <file://%s>' % urllib.pathname2url(path))
			os.system('/usr/bin/xdg-open \"%s\"' % path)
			ret = True
			break
	return ret

		
