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

import re, logging, os

APP_NAME = 'RBLyrics'
TOKEN_STRIP = {'\([^\)]*\)':'', '[\ -]+':' '}
LRC_PATH_TEMPLATE = ['%s/%s.lrc', '%s - %s.lrc']

log = logging.getLogger(APP_NAME)
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('RBLyrics %(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
log.addHandler(console_handler)

class SongInfo:
	def __init__(self, artist, title):
		self.__info = {'ti':title, 'ar':artist}
		return
	
	def __str__(self):
		return '(%s - %s)' % (self.__info['ar'], self.__info['ti'])
		
	def __eq__(self, other):
		ret = False
		for k in self.__info.keys():
			if self.__info[k] != other.get(k):
				break
		else:
			ret = True
		return ret
		
	def get(self, key):
		return self.__info[key]

class LyricsInfo:
	def __init__(self, raw):
		self.__raw = raw
		self.__info = {'ar':'', 'ti':''}
		self.__content = {}
		self.__parse()
		return
	
	def __parse(self):
		log.debug('enter')
		lines = self.__raw.split(os.linesep)
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
				self.__info['ti'] = m.groups()[0]
			# search for artist property
			m = re_ar.search(line)
			if not m is None:
				self.__info['ar'] = m.groups()[0]
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
				lrc = line[pos:]
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
			if second in self.__content:
				self.__content[second] += cache[key]
			else:
				self.__content[second] = cache[key]
		log.debug('leave')
		return
		
	def get(self, key):
		return self.__info[key]
		
	def get_raw(self):
		return self.__raw
	
	def get_line(self, timestamp):
		try:
			line = self.__content[timestamp]
		except:
			line = None
		return line
		
def clean_token(token):
	log.debug('enter (%s)' % token)
	result = token.lower()
	for strip in TOKEN_STRIP.keys():
		result = re.sub(strip, TOKEN_STRIP[strip], result)
	result = result.strip()
	log.debug('leave (%s)' % result)
	return result

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
	
def distance(songinfo, lyrics):
	return edit_distance(songinfo.get('ar').lower(), lyrics.get('ar').lower()) + edit_distance(songinfo.get('ti').lower(), lyrics.get('ti').lower())
	
def save_lyrics(root, songinfo, lyrics):
	log.debug('enter')
	path = os.path.join(root, LRC_PATH_TEMPLATE[0] % (songinfo.get('ar'), songinfo.get('ti')))
	dir = os.path.dirname(path)
	if not os.path.exists(dir):
		os.makedirs(dir)
	open(path, 'w').write(lyrics.get_raw())
	log.debug('leave')
	return

def load_lyrics(root, songinfo):
	log.debug('enter')
	lyrics = None
	for p in LRC_PATH_TEMPLATE:
		path = os.path.join(root, p % (songinfo.get('ar'), songinfo.get('ti')))
		if os.path.exists(path):
			log.info('load <%s>' % path)
			lyrics = LyricsInfo(open(path, 'r').read())
			break
	log.debug('leave')
	return lyrics
	
def open_lyrics(root, songinfo):
	log.debug('enter')
	ret = False
	for p in LRC_PATH_TEMPLATE:
		path = os.path.join(root, p % (songinfo.get('ar'), songinfo.get('ti')))
		if os.path.exists(path):
			log.info('open <%s>' % path)
			os.system('/usr/bin/xdg-open \"%s\"' % path)
			ret = True
			break
	log.debug('leave')
	return ret

		
