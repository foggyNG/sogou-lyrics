#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import os, logging, re
from datetime import datetime, timedelta
from utils import edit_distance

LRC_PATH_TEMPLATE = ['%s/%s.lrc', '%s - %s.lrc']

def init_song_search(prefs, artist, title):
	ret = Song()
	ret.prefs_ = prefs
	ret.songinfo_ = {'ar':artist, 'ti':title}
	for i in LRC_PATH_TEMPLATE:
		ret.path_.append(i % (artist, title))
	return ret

def init_song_result(song, raw):
	ret = Song()
	ret.prefs_ = song.prefs_
	ret.songinfo_ = song.songinfo_
	for i in LRC_PATH_TEMPLATE:
		ret.path_.append(i % (ret.songinfo_['ar'], ret.songinfo_['ti']))
	ret.raw_ = raw
	ret.parse_lyrics()
	return ret

def song_cmp(x, y):
	return x.edit_distance_ - y.edit_distance_
	
class Song:
	def __init__(self):
		self.prefs_ = None
		self.songinfo_ = {}
		self.path_ = []
		self.lrcinfo_ = {}
		self.lrc_ = {}
		self.raw_ = ''
		self.edit_distance_ = 0
		self.__last_update = datetime.fromtimestamp(0)
		return
		
	def save_lyrics(self):
		path = os.path.join(self.prefs_.get('folder'), self.path_[0])
		dir = os.path.dirname(path)
		if not os.path.exists(dir):
			os.makedirs(dir)
		open(path, 'w').write(self.raw_)
		return
		
	def load_lyrics(self):
		ret = False
		if self.lrc_ != {}:
			ret = True
		elif datetime.now() - self.__last_update < timedelta(seconds = 5):
			ret = False
		else:
			self.__last_update = datetime.now()
			for p in self.path_:
				path = os.path.join(self.prefs_.get('folder'), p)
				if os.path.isfile(path):
					logging.info('load <%s>' % path)
					self.raw_ = open(path).read()
					self.parse_lyrics()
					ret = True
					break
		return ret
		
	def open_lyrics(self):
		ret = False
		for p in self.path_:
			path = os.path.join(self.prefs_.get('folder'), p)
			if os.path.exists(path):
				logging.info('open <%s>' % path)
				os.system('/usr/bin/xdg-open \"%s\"' % path)
				ret = True
				break
		return ret
		
	def parse_lyrics(self):
		logging.debug('enter')
		lines = self.raw_.split(os.linesep)
		self.lrc_ = {}
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
				self.lrcinfo_['ti'] = m.groups()[0]
			# search for artist property
			m = re_ar.search(line)
			if not m is None:
				self.lrcinfo_['ar'] = m.groups()[0]
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
					#logging.debug(time)
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
						logging.error('invalid timestamp %s' % time)
		tags = cache.keys()
		tags.sort()
		for key in tags:
			second = int(round((key + offset) / 1000.0))
			if second in self.lrc_:
				self.lrc_[second] += cache[key]
			else:
				self.lrc_[second] = cache[key]
		del cache, lines
		# calculate edit distance
		ar = ''
		ti = ''
		if self.lrcinfo_.has_key('ar'):
			ar = self.lrcinfo_['ar']
		if self.lrcinfo_.has_key('ti'):
			ti = self.lrcinfo_['ti']
		self.edit_distance_ = edit_distance(ar, self.songinfo_['ar']) + edit_distance(ti, self.songinfo_['ti'])
		logging.debug('edit distance = %d' % self.edit_distance_)
		logging.debug('leave')
		return
