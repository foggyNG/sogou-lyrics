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
#  Utilities.

import re, logging, os, sys, urllib, gettext
from chardet import detect
_ = gettext.gettext

## Pattern for token strip.
TOKEN_STRIP = {'\([^\)]*\)':'', '[\ -]+':' '}

## Pattern for generate lyrics path.
LRC_PATH_TEMPLATE = ['%s/%s.lrc', '%s - %s.lrc']

## Logging system.
log = logging.getLogger('RBLyrics')

#
re_ti = re.compile(r'\[ti:([^\]]*)\]')
re_ar = re.compile(r'\[ar:([^\]]*)\]')
re_offset = re.compile(r'\[offset:([+-]{0,1}[0-9]+)\]')
re_time = re.compile(r'\[(?P<min>[0-9]{2}):(?P<sec>[0-9]{2})(\.(?P<milli>[0-9]{1,3}))?\]')

		
## Song information.
class SongInfo(object):
	
	## The constructor.
	#  @param artist Artist.
	#  @param title Title.
	def __init__(self, artist, title):
		self._artist = artist
		self._title = title
		return
	
	def __str__(self):
		return '%s - %s' % (self._artist, self._title)
		
	def __eq__(self, other):
		return self._title == other.ti and self._artist == other.ar

	ar = property(lambda self: self._artist)
	ti = property(lambda self: self._title)
	
## Lyrics information.
class LyricsInfo(object):
	
	## The constructor.
	#  @param raw Lyrics raw content.
	def __init__(self, raw):
		self._raw = raw
		self._artist = ''
		self._title = ''
		self._content = {}
		self._parse()
		return
	
	def _make_time(self, group):
		min = int(group.group('min'))
		sec = int(group.group('sec'))
		milli = group.group('milli')
		if milli:
			milli = int(milli) * pow(10, 3-len(milli))
		else:
			milli = 0
		return min*60000 + sec*1000 + milli
		
	## Parse lyrics raw content.
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
		
	ar = property(lambda self: self._artist)
	ti = property(lambda self: self._title)
	raw = property(lambda self: self._raw)
	content = property(lambda self: self._content)
	
## Clean token.
#  @param token Original token.
#  @return Cleaned token.
def clean_token(token):
	result = token.lower()
	for strip in TOKEN_STRIP.keys():
		result = re.sub(strip, TOKEN_STRIP[strip], result)
	result = result.strip()
	return result

## Calculate edit distance.
#  @param left Instance A.
#  @param right Instance B.
#  @return Edit distance between A and B.
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

## Calculate edit distance between songinfo and lyrics.
#  @param songinfo Song information.
#  @param lyrics Lyrics information.
#  @return Edit distance between songinfo and lyrics.
def distance(songinfo, lyrics):
	return edit_distance(songinfo.ar.lower(), lyrics.ar.lower()) + edit_distance(songinfo.ti.lower(), lyrics.ti.lower())

## Save lyrics to file.
#  @param root Lyrics root directory.
#  @param songinfo Song information of the lyrics.
#  @param lyrics Lyrics information.
def save_lyrics(root, pattern, songinfo, lyrics):
	path = os.path.join(root, pattern % (songinfo.ar, songinfo.ti))
	dir = os.path.dirname(path)
	if not os.path.exists(dir):
		os.makedirs(dir)
	open(path, 'w').write(lyrics.raw)
	log.info('save <file://%s>' % urllib.pathname2url(path))
	return

## Load lyrics from file.
#  @param root Lyrics root directory.
#  @param songinfo Song information of the lyrics.
#  @return Lyrics information.
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
					encoding = detect(l)
					if encoding:
						charset = encoding['encoding']
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

## Open lyrics file in system default editor.
#  @param root Lyrics root directory.
#  @param songinfo Song information of the lyrics.
#  @return If successed.
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

		
