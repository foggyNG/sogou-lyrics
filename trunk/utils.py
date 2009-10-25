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

def detect_charset(s):
	charsets = ('iso-8859-1', 'gbk', 'utf-8')
	for charset in charsets:
		try:
			return unicode(unicode(s, 'utf-8').encode(charset), 'gbk')
		except:
			continue
	return s

def parse_lyrics(lines):
	logging.debug('enter')
	content = {}
	cache = {}
	re_ti = re.compile('\[ti:[^\]]*\]')
	re_ar = re.compile('\[ar:[^\]]*\]')
	re_offset = re.compile('\[offset:[^\]]*\]')
	re_lrc = re.compile('(\[[0-9\.:]*\])+.*')
	re_time = re.compile('\[[0-9]{2}:[0-9]{2}\.[0-9]{2}\]')
	offset = 0
	for line in lines:
		# search for title property
		m = re_ti.search(line)
		if not m is None:
			segment = m.group(0)
			content['ti'] = segment[4:-1]
		# search for artist property
		m = re_ar.search(line)
		if not m is None:
			segment = m.group(0)
			content['ar'] = segment[4:-1]
		# search for offset property
		m = re_offset.search(line)
		if not m is None:
			segment = m.group(0)
			offset = int(segment[8:-1])
		# parse lrc
		m = re_lrc.match(line)
		if not m is None:
			pos = 0
			tm = re_time.findall(line)
			for time in tm:
				pos = pos + len(time)
			lrc = m.group(0)[pos:]
			for time in tm:
				try:
					minute = int(time[1:3])
					second = int(time[4:6])
					centi = int(time[7:9])
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
	del cache
	logging.debug('leave')
	return content

def clean_token(token):
	result = token.lower()
	for strip in TOKEN_STRIP.keys():
		result = re.sub(strip, TOKEN_STRIP[strip], result)
	return result
	
def verify_lyrics(content, artist, title):
	logging.debug('enter')
	retval = 0
	ar = ''
	ti = ''
	if content.has_key('ar'):
		ar = content['ar']
	if content.has_key('ti'):
		ti = content['ti']
	retval = edit_distance(ar, artist) + edit_distance(ti, title)
	logging.debug('leave')
	return retval

def load_lyrics(lrc_path):
	logging.debug('enter')
	lrc = {}
	for i in lrc_path:
		if os.path.isfile(i):
			logging.debug('loading <%s>' % i)
			lrc = parse_lyrics(open(i, 'r').readlines())
			break
	logging.debug('leave')
	return lrc

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
