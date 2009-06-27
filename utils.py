import os, re

TOKEN_STRIP = {'\([^\)]*\)':'', '[\ -]+':' '}

def detect_charset(s):
	charsets = ('iso-8859-1', 'gbk', 'utf-8')
	for charset in charsets:
		try:
			return unicode(unicode(s, 'utf-8').encode(charset), 'gbk')
		except:
			continue
	return s

def parse_lyrics(lines):
	print 'enter'
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
					print 'invalid timestamp %s' % time
	tags = cache.keys()
	tags.sort()
	for key in tags:
		second = int(round((key + offset) / 1000.0))
		if second in content:
			content[second] += cache[key]
		else:
			content[second] = cache[key]
	del cache
	print 'leave'
	return content

def clean_token(token):
	result = token.lower()
	for strip in TOKEN_STRIP.keys():
		result = re.sub(strip, TOKEN_STRIP[strip], result)
	return result
	
def verify_lyrics(content, artist, title):
	print 'enter'
	retval = 0
	if not content.has_key('ar'):
		print 'cannot find artist in lyrics'
	elif not content.has_key('ti'):
		print 'cannot find title in lyrics'
	else:
		ar = content['ar']
		ti = content['ti']
		print '%s - %s' % (ar, ti)
		ar = clean_token(ar)
		ti = clean_token(ti)
		ar1 = clean_token(artist)
		ti1 = clean_token(title)
		if ar.find(ar1) != -1 and ti.find(ti1) != -1:
			retval = 1
	print 'leave'
	return retval

def load_lyrics(lrc_path, artist, title):
	lrc = {}
	if os.path.exists(lrc_path) and os.path.isfile(lrc_path):
		lrc = parse_lyrics(open(lrc_path, 'r').readlines())
		'''if not verify_lyrics(lrc, artist, title):
			lrc = {}
			print 'broken lyrics file %s moved to %s.bak' % (lrc_path, lrc_path)
			try:
				os.rename(lrc_path, '%s.bak' % lrc_path)
			except OSError:
				print 'move broken lyrics file failed'
		'''
	return lrc
