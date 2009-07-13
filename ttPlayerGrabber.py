#!/usr/bin/env python
#-*- coding: UTF-8 -*-
# Filename: ttPlayer.py

import re, random, urllib, logging
import codecs
from utils import *

class ttpClient:
    '''
    privide ttplayer specific function, such as encoding artist and title,
    generate a Id code for server authorizition.
    (see http://ttplyrics.googlecode.com/svn/trunk/crack) 
    '''
    @staticmethod
    def CodeFunc(Id, data):
	'''
	Generate a Id Code
	These code may be ugly coz it is translated
	from C code which is translated from asm code
	grabed by ollydbg from ttp_lrcs.dll.
	(see http://ttplyrics.googlecode.com/svn/trunk/crack) 
	'''
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
	str = str.encode('UTF-16')[2:]
	for i in range(len(str)):
	    rtn += '%02x' % ord(str[i])

	return rtn
	
class ttPlayerGrabber:
	
	def __init__(self, artist, title):
		self.artist = artist
		self.title = title
		self.netEncoder= 'utf-8'
		self.locale = 'utf-8'
		return
		
	
	def parse(self,a):
		b=[]
		for i in a:
			c=re.search('id=\"(.*?)\" artist=\"(.*?)\" title=\"(.*?)\"',i)
			try:
				_artist=c.group(2)
				_title=c.group(3)
				_id=c.group(1)
			except:
				pass
			else:
				url='http://lrcct2.ttplayer.com/dll/lyricsvr.dll?dl?Id=%d&Code=%d&uid=01&mac=%012x' %(int(_id),ttpClient.CodeFunc(int(_id),(_artist+_title)), random.randint(0,0xFFFFFFFFFFFF))
				b.append([_artist,_title,url])
		return b
	
	def search(self):
		logging.debug('enter')
		retval = []
		url='http://lrcct2.ttplayer.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' %(ttpClient.EncodeArtTit(unicode(self.artist,self.locale).replace(u' ','').lower()), ttpClient.EncodeArtTit(unicode(self.title,self.locale).replace(u' ','').lower()))
		logging.info('search uri <%s>' % url)
		try:
			file=urllib.urlopen(url,None,None)
			webInfo=file.read()
			file.close()
		except IOError:
			pass
		else:
			tmpList=re.findall(r'<lrc.*?</lrc>',webInfo)
			for instance in self.parse(tmpList):
				try:
					logging.info('lyrics file <%s>' % instance[2])
					cache = urllib.urlopen(instance[2]).readlines()
					lrc = []
					for line in cache:
						lrc.append(line.decode('utf-8').encode('utf-8'))
					retval.append(lrc)
				except IOError:
					pass
		logging.debug('leave')
		return retval

