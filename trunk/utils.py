#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, re, logging, urllib2

TOKEN_STRIP = {'\([^\)]*\)':'', '[\ -]+':' '}
LRC_PATH_TEMPLATE = ['%s/%s/%s.lrc', '%s/%s - %s.lrc']

def gen_lrc_path(dir, artist, title):
	ret = []
	for i in LRC_PATH_TEMPLATE:
		ret.append(i % (dir, artist, title))
	return ret

def load_lyrics(paths):
	logging.debug('enter')
	ret = {}
	for p in paths:
		if os.path.isfile(p):
			ret = parse_lyrics(open(p).read())
			break
	logging.debug('leave')
	return ret
	
def parse_lyrics(content):
	logging.debug('enter')
	lines = content.split(os.linesep)
	content = {}
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
			content['ti'] = m.groups()[0]
		# search for artist property
		m = re_ar.search(line)
		if not m is None:
			content['ar'] = m.groups()[0]
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
		if second in content:
			content[second] += cache[key]
		else:
			content[second] = cache[key]
	del cache, lines
	logging.debug('leave')
	return content

def clean_token(token):
	result = token.lower()
	for strip in TOKEN_STRIP.keys():
		result = re.sub(strip, TOKEN_STRIP[strip], result)
	return result
	
def verify_lyrics(content, lrcinfo):
	logging.debug('enter')
	retval = 0
	ar = ''
	ti = ''
	if content.has_key('ar'):
		ar = content['ar']
	if content.has_key('ti'):
		ti = content['ti']
	retval = edit_distance(ar, lrcinfo['ar']) + edit_distance(ti, lrcinfo['ti'])
	logging.debug('leave')
	return retval

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

def gen_lrc_instance(content, lrcinfo):
	lrc_content = parse_lyrics(content)
	dist = verify_lyrics(lrc_content, lrcinfo)
	artist = ''
	title = ''
	if lrc_content.has_key('ar'):
		artist = lrc_content['ar']
	if lrc_content.has_key('ti'):
		title = lrc_content['ti']
	return [dist, artist, title, content]
