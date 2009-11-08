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

## @package RBLyrics.engine.ttplayer
#  TTPlayer search engine.

import random, urllib2, logging, threading
from xml.dom.minidom import parseString
from optparse import OptionParser

from chardet import detect
log = logging.getLogger('RBLyrics')

## TTPlayer lyrics server crack functionality.
#
#  Provide ttplayer specific function, such as encoding artist and title,
#  generate a Id code for server authorizition.
#  (see http://ttplyrics.googlecode.com/svn/trunk/crack) 
class ttpClient:

	## Generate a Id Code.
	#  These code may be ugly coz it is translated
	#  from C code which is translated from asm code
	#  grabed by ollydbg from ttp_lrcs.dll.
	#  (see http://ttplyrics.googlecode.com/svn/trunk/crack)
    @staticmethod
    def CodeFunc(Id, data):
	length = len(data)

	tmp2=0
	tmp3=0

	tmp1 = (Id & 0x0000FF00) >> 8							#右移8位后为x0000015F

	    #tmp1 0x0000005F
	if ( (Id & 0x00FF0000) == 0 ):
	    tmp3 = 0x000000FF & ~tmp1							#CL 0x000000E7
	else:
	    tmp3 = 0x000000FF & ((Id & 0x00FF0000) >> 16)                               #右移16后为x00000001

	tmp3 = tmp3 | ((0x000000FF & Id) << 8)                                          #tmp3 0x00001801
	tmp3 = tmp3 << 8                                                                #tmp3 0x00180100
	tmp3 = tmp3 | (0x000000FF & tmp1)                                               #tmp3 0x0018015F
	tmp3 = tmp3 << 8                                                                #tmp3 0x18015F00
	if ( (Id & 0xFF000000) == 0 ) :
	    tmp3 = tmp3 | (0x000000FF & (~Id))                                          #tmp3 0x18015FE7
	else :
	    tmp3 = tmp3 | (0x000000FF & (Id >> 24))                                     #右移24位后为0x00000000

	#tmp3	18015FE7
        
	i=length-1
	while(i >= 0):
	    char = ord(data[i])
	    if char >= 0x80:
		char = char - 0x100
	    tmp1 = (char + tmp2) & 0x00000000FFFFFFFF
	    tmp2 = (tmp2 << (i%2 + 4)) & 0x00000000FFFFFFFF
	    tmp2 = (tmp1 + tmp2) & 0x00000000FFFFFFFF
	    #tmp2 = (ord(data[i])) + tmp2 + ((tmp2 << (i%2 + 4)) & 0x00000000FFFFFFFF)
	    i -= 1

	#tmp2 88203cc2
	i=0
	tmp1=0
	while(i<=length-1):
	    char = ord(data[i])
	    if char >= 128:
		char = char - 256
	    tmp7 = (char + tmp1) & 0x00000000FFFFFFFF
	    tmp1 = (tmp1 << (i%2 + 3)) & 0x00000000FFFFFFFF
	    tmp1 = (tmp1 + tmp7) & 0x00000000FFFFFFFF
	    #tmp1 = (ord(data[i])) + tmp1 + ((tmp1 << (i%2 + 3)) & 0x00000000FFFFFFFF)
	    i += 1

	#EBX 5CC0B3BA

	#EDX = EBX | Id
	#EBX = EBX | tmp3
	tmp1 = (((((tmp2 ^ tmp3) & 0x00000000FFFFFFFF) + (tmp1 | Id)) & 0x00000000FFFFFFFF) * (tmp1 | tmp3)) & 0x00000000FFFFFFFF
	tmp1 = (tmp1 * (tmp2 ^ Id)) & 0x00000000FFFFFFFF

	if tmp1 > 0x80000000:
	    tmp1 = tmp1 - 0x100000000
	return tmp1
    
    @staticmethod
    def EncodeArtTit(str):
	rtn = ''
	str = str.encode('UTF-16', 'ignore')[2:]
	for i in range(len(str)):
	    rtn += '%02x' % ord(str[i])

	return rtn

## QianQian player engine.
#
#  Retrieve lyrics from www.ttplayer.com.
class TTPlayer:

	## @var _timeout
	#  HTTP request timeout.
	
	## @var _max
	#  Max number of lyrics expected.
	
	## @var _candidate
	#  Lyrics candidates.
	
	## @var _lock
	#  Thread lock for appending _candidate list.
	
	## The constructor.
	#  @param timeout HTTP request timeout.
	#  @param max Max number of lyrics expected.
	def __init__(self, timeout = 3, max = 5):
		log.debug('enter')
		self._timeout = timeout
		self._max = max
		self._candidate = []
		self._lock = threading.Condition(threading.Lock())
		log.debug('leave')
		return
	
	## Lyrics receive handler.
	#  @param url Lyrics url.
	def _receive_lyrics(self, url):
		log.debug('enter')
		try:
			cache = urllib2.urlopen(url, None, self._timeout).read()
		except Exception as e:
			log.error(e)
		else:
			encoding = detect(cache)['encoding']
			cache = cache.decode(encoding, 'ignore').encode('UTF-8', 'ignore')
			log.info('lyrics <%s>' % url)
			self._lock.acquire()
			self._candidate.append(cache)
			self._lock.release()
		log.debug('leave')
		return
		
	## Retrieve lyrics.
	#  @param artist Song artist.
	#  @param title Song title.
	#  @return Lyrics candidates.
	def search(self, artist, title):
		log.debug('enter')
		retval = []
		artist_token = ttpClient.EncodeArtTit(artist.replace(' ','').lower())
		title_token = ttpClient.EncodeArtTit(title.replace(' ','').lower())
		url='http://lrcct2.ttplayer.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' %(artist_token, title_token)
		log.debug('search url <%s>' % url)
		try:
			xml = urllib2.urlopen(url, None, self._timeout).read()
			elements = parseString(xml).getElementsByTagName('lrc')
		except Exception as e:
			log.error(e)
		else:
			threads = []
			for element in elements:
				artist = element.getAttribute('artist')
				title = element.getAttribute('title')
				id = int(element.getAttribute('id'))
				url = 'http://lrcct2.ttplayer.com/dll/lyricsvr.dll?dl?Id=%d&Code=%d&uid=01&mac=%012x' %(id,ttpClient.CodeFunc(id,(artist+title).encode('UTF-8', 'ignore')), random.randint(0,0xFFFFFFFFFFFF))
				threads.append(threading.Thread(target=self._receive_lyrics, args=(url,)))
				if len(threads) >= self._max:
					break
			for t in threads:
				t.start()
			for t in threads:
				t.join()
			log.info('%d candidates found' % len(self._candidate))
		log.debug('leave')
		return self._candidate
		
if __name__ == '__main__':
	log.setLevel(logging.DEBUG)
	handler = logging.StreamHandler()
	handler.setFormatter(logging.Formatter('%(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
	log.addHandler(handler)
	parser = OptionParser()
	parser.add_option('-a', '--artist', dest = 'artist', type = 'string', help = 'song artist')
	parser.add_option('-i', '--title', dest = 'title', type = 'string', help = 'song title')
	parser.add_option('-t', '--timeout', dest = 'timeout', type = 'int', help = 'url request timeout')
	parser.add_option('-m', '--max', dest = 'max', type = 'int', help = 'max number of expected')
	parser.set_defaults(timeout = 3, max = 5)
	(options, args) = parser.parse_args()
	if len(args) != 0:
		parser.error("incorrect number of arguments")
	elif options.artist is None:
		parser.error('artist is required')
	elif options.title is None:
		parser.error('title is required')
	else:
		engine = TTPlayer(options.timeout, options.max)
		candidate = engine.search(options.artist, options.title)
		for c in candidate:
			log.info('candidate:\n%s' % c)
			
