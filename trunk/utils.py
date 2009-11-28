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
_ = gettext.gettext

## Pattern for token strip.
TOKEN_STRIP = {'\([^\)]*\)':'', '[\ -]+':' '}

## Pattern for generate lyrics path.
LRC_PATH_TEMPLATE = ['%s/%s.lrc', '%s - %s.lrc']

## Logging system.
log = logging.getLogger('RBLyrics')

## Song information.
class SongInfo:
	
	## @var _info
	#  Song information dict.
	
	## The constructor.
	#  @param artist Artist.
	#  @param title Title.
	def __init__(self, artist, title):
		self._info = {'ti':title, 'ar':artist}
		return
	
	def __str__(self):
		return '(%s - %s)' % (self._info['ar'], self._info['ti'])
		
	def __eq__(self, other):
		ret = False
		for k in self._info.keys():
			if self._info[k] != other.get(k):
				break
		else:
			ret = True
		return ret
	
	## Get information.
	#  @param key Key of the information.
	#  @return Information to the key.
	def get(self, key):
		return self._info[key]

## Lyrics information.
class LyricsInfo:
	
	## @var _raw
	#  Raw lyrics content.
	
	## @var _info
	#  Lyrics information.
	
	## @var _content
	#  Parsed lyrics content.
	
	## The constructor.
	#  @param raw Lyrics raw content.
	def __init__(self, raw):
		self._raw = raw
		self._info = {'ar':'', 'ti':''}
		self._content = {}
		self._parse()
		return
	
	## Parse lyrics raw content.
	def _parse(self):
		log.debug('enter')
		lines = self._raw.split(os.linesep)
		cache = {}
		re_ti = re.compile('\[ti:([^\]]*)\]')
		re_ar = re.compile('\[ar:([^\]]*)\]')
		re_offset = re.compile('\[offset:([^\]]*)\]')
		re_lrc = re.compile('(\[[0-9\.:]*\])+.*')
		re_time = re.compile('(\[([0-9]{2}):([0-9]{2})\.?([0-9]{2})?\])')
		offset = 0
		for line in lines:
			# search for title property
			m = re_ti.search(line)
			if not m is None:
				self._info['ti'] = m.groups()[0]
			# search for artist property
			m = re_ar.search(line)
			if not m is None:
				self._info['ar'] = m.groups()[0]
			# search for offset property
			m = re_offset.search(line)
			if not m is None:
				offset = int(m.groups()[0])
			# parse lrc
			m = re_lrc.match(line)
			if not m is None:
				pos = 0
				tm = re_time.findall(line)
				for time in tm:
					pos = pos + len(time[0])
				lrc = line[pos:].strip()
				if len(lrc) == 0:
					# ignore blank line
					continue
				for time in tm:
					#log.debug(time)
					try:
						minute = int(time[1])
						second = int(time[2])
						try:
							centi = int(time[3])
						except:
							centi = 0
						key = (minute * 60 + second) * 1000 + centi * 10
						cache[key] = lrc
					except ValueError:
						log.error('invalid timestamp %s' % time)
		tags = cache.keys()
		tags.sort()
		for key in tags:
			second = int(round((key + offset) / 1000.0))
			if second in self._content:
				self._content[second] += cache[key]
				self._content[second].replace(os.linesep, ' ')
			else:
				self._content[second] = cache[key]
		log.debug('leave')
		return
	
	## Get lyrics information.
	#  @param key Key of the information.
	#  @return Information to the key.
	def get(self, key):
		return self._info[key]
	
	## Get raw lyrics content.
	#  @return Raw lyrics content.
	def get_raw(self):
		return self._raw
	
	## Get lyrics line.
	#  @param timestamp Timestamp of the line.
	#  @return Content to the timestamp, None for missed.
	def get_line(self, timestamp):
		try:
			line = self._content[timestamp]
		except:
			line = None
		return line

## Clean token.
#  @param token Original token.
#  @return Cleaned token.
def clean_token(token):
	log.debug('enter (%s)' % token)
	result = token.lower()
	for strip in TOKEN_STRIP.keys():
		result = re.sub(strip, TOKEN_STRIP[strip], result)
	result = result.strip()
	log.debug('leave (%s)' % result)
	return result

## Calculate edit distance.
#  @param left Instance A.
#  @param right Instance B.
#  @return Edit distance between A and B.
def edit_distance(left, right):
	log.debug('enter (%s, %s)' % (left, right))
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
	log.debug('leave (%d)' % dist[m][n])
	return dist[m][n]

## Calculate edit distance between songinfo and lyrics.
#  @param songinfo Song information.
#  @param lyrics Lyrics information.
#  @return Edit distance between songinfo and lyrics.
def distance(songinfo, lyrics):
	return edit_distance(songinfo.get('ar').lower(), lyrics.get('ar').lower()) + edit_distance(songinfo.get('ti').lower(), lyrics.get('ti').lower())

## Save lyrics to file.
#  @param root Lyrics root directory.
#  @param songinfo Song information of the lyrics.
#  @param lyrics Lyrics information.
def save_lyrics(root, pattern, songinfo, lyrics):
	log.debug('enter')
	path = os.path.join(root, pattern % (songinfo.get('ar'), songinfo.get('ti')))
	dir = os.path.dirname(path)
	if not os.path.exists(dir):
		os.makedirs(dir)
	open(path, 'w').write(lyrics.get_raw())
	log.info('save <file://%s>' % urllib.pathname2url(path))
	log.debug('leave')
	return

## Load lyrics from file.
#  @param root Lyrics root directory.
#  @param songinfo Song information of the lyrics.
#  @return Lyrics information.
def load_lyrics(root, songinfo):
	log.debug('enter')
	lyrics = None
	for p in LRC_PATH_TEMPLATE:
		path = os.path.join(root, p % (songinfo.get('ar'), songinfo.get('ti')))
		if os.path.exists(path):
			log.info('load <file://%s>' % urllib.pathname2url(path))
			lyrics = LyricsInfo(open(path, 'r').read())
			break
	log.debug('leave')
	return lyrics

## Open lyrics file in system default editor.
#  @param root Lyrics root directory.
#  @param songinfo Song information of the lyrics.
#  @return If successed.
def open_lyrics(root, songinfo):
	log.debug('enter')
	ret = False
	for p in LRC_PATH_TEMPLATE:
		path = os.path.join(root, p % (songinfo.get('ar'), songinfo.get('ti')))
		if os.path.exists(path):
			log.info('open <file://%s>' % urllib.pathname2url(path))
			os.system('/usr/bin/xdg-open \"%s\"' % path)
			ret = True
			break
	log.debug('leave')
	return ret

		
