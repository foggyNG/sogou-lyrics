#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import os, re
from utils import edit_distance, log

LRC_PATH_TEMPLATE = ['%s/%s.lrc', '%s - %s.lrc']

def init_song_search(prefs, artist, title):
	log.debug('enter')
	ret = Song()
	ret.prefs_ = prefs
	ret.songinfo_ = {'ar':artist, 'ti':title}
	for i in LRC_PATH_TEMPLATE:
		ret.path_.append(i % (artist, title))
	log.debug('leave')
	return ret

def init_song_result(song, raw):
	log.debug('enter')
	ret = Song()
	ret.prefs_ = song.prefs_
	ret.songinfo_ = song.songinfo_
	for i in LRC_PATH_TEMPLATE:
		ret.path_.append(i % (ret.songinfo_['ar'], ret.songinfo_['ti']))
	ret.raw_ = raw
	ret.parse_lyrics()
	log.debug('leave')
	return ret

def song_cmp(x, y):
	return x.edit_distance_ - y.edit_distance_
	
class Song:
	def __init__(self):
		log.debug('enter')
		self.prefs_ = None
		self.songinfo_ = {}
		self.path_ = []
		self.lrcinfo_ = {}
		self.lrc_ = {}
		self.raw_ = ''
		self.edit_distance_ = 0
		log.debug('leave')
		return
		
	def save_lyrics(self):
		log.debug('enter')
		path = os.path.join(self.prefs_.get('folder'), self.path_[0])
		dir = os.path.dirname(path)
		if not os.path.exists(dir):
			os.makedirs(dir)
		open(path, 'w').write(self.raw_)
		log.debug('leave')
		return
		
	def load_lyrics(self):
		log.debug('enter')
		ret = False
		if self.lrc_ != {}:
			ret = True
		else:
			for p in self.path_:
				path = os.path.join(self.prefs_.get('folder'), p)
				if os.path.isfile(path):
					log.info('load <%s>' % path)
					self.raw_ = open(path).read()
					self.parse_lyrics()
					ret = True
					break
		log.debug('leave')
		return ret
		
	def open_lyrics(self):
		log.debug('enter')
		ret = False
		for p in self.path_:
			path = os.path.join(self.prefs_.get('folder'), p)
			if os.path.exists(path):
				log.info('open <%s>' % path)
				os.system('/usr/bin/xdg-open \"%s\"' % path)
				ret = True
				break
		log.debug('leave')
		return ret
		
	def parse_lyrics(self):
		log.debug('enter')
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
		self.edit_distance_ = edit_distance(ar.lower(), self.songinfo_['ar'].lower()) + edit_distance(ti.lower(), self.songinfo_['ti'].lower())
		log.debug('leave')
		return
