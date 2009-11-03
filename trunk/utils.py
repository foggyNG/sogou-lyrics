#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import re, logging

APP_NAME = 'RBLyrics'
TOKEN_STRIP = {'\([^\)]*\)':'', '[\ -]+':' '}

log = logging.getLogger(APP_NAME)

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
	
