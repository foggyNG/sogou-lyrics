#!/usr/bin/python
# -*- encoding: utf8 =*-

import os
import urllib2
from HTMLParser import HTMLParser

#log = open("log.log", "w+")
def DetectCharset(s):
	charsets = ('gbk', 'gb18030', 'gb2312', 'iso-8859-1', 'utf-16', 'utf-8', 'utf-32', 'ascii')
	for charset in charsets:
		try:
			return unicode(s, charset)
		except:
			continue
	return s
	
class MySearchParser(HTMLParser):
	lyricArtists = []
	lyricTitles = []
	lyricUrls = []
	state = 0
	SongInfo = ""
	url = ""
	def handle_starttag(self, tag, attrs):
		if self.state == 0 and tag == 'div':
			for k,v in attrs:
				if k == "id" and v == 'res':
					self.state = 1
					break
		elif self.state == 1 and tag == 'li':
			self.state = 2
		elif self.state == 2 and tag == 'a':
			self.state = 3
			for k,v in attrs:
				if k == "href":
					self.url = v
					break
		
	
	def handle_data(self,data):
		if self.state != 3:
			return
		self.SongInfo += data
		#print "    %s   %d(%s, %s)" % (data, self.isBefore, self.before, self.after)
					
		
	
	def handle_endtag(self,tag):
		if self.state == 3 and tag == 'a':
			self.state = 1
			self.state = 0
			info = self.SongInfo.split('[')
			title = ''
			artist = ''
			for v in info:
				if v[0:3] == 'ti:':
					title = v[3:-2]
				elif v[0:3] == 'ar:':
					artist = v[3:-2]
			self.lyricTitles.append(title)
			self.lyricArtists.append(artist)
			self.lyricUrls.append(self.url)
				
			#print unicode(self.SongInfo, "utf8").encode("gbk")
			self.SongInfo = ''
	
	def dumpInfo(self, title, artist):
		index = 0
		for t in self.lyricTitles:
			if t.find(title) >= 0 and self.lyricArtists[index].find(artist) >= 0:
				#tmp = "作者：%s\n歌名：%s\nURL：%s\n" % (self.lyricArtists[index], t, self.lyricUrls[index])
				#print unicode(tmp, "utf8").encode("gbk")
				f = open("%d" % index, 'w+')
				f.write(DownLyric(self.lyricUrls[index]))
				f.close()
			index += 1
	def save(self, filename):
		f = open(filename, 'w+')
		f.write('<?xml version="1.0" encoding="UTF-8" ?>\n');
		index = 0
		f.write('<result>\n')
		for url in self.lyricUrls:
			f.write('\t<lrc id="%s" artist="%s" title="%s"></lrc>\n' % (self.lyricUrls[index], self.lyricArtists[index], self.lyricTitles[index]))
			index = index + 1
		f.write('</result>\n')
		f.close()

	def dumpXML(self):
		xml = '<?xml version="1.0" encoding="UTF-8" ?>\n'
		index = 0
		xml += '<result>\n'
		for url in self.lyricUrls:
			xml += '\t<lrc id="%s" artist="%s" title="%s"></lrc>\n' % (self.lyricUrls[index], self.lyricArtists[index], self.lyricTitles[index])
			index = index + 1
		xml += '</result>\n'
		return xml
        
	def dump(self):
		txt = ''
		index = 0
		for url in self.lyricUrls:
			txt += 'artist=%s\ntitle=%s\nid=%s\n' % (self.lyricArtists[index], self.lyricTitles[index], self.lyricUrls[index])
			index = index + 1
		return txt

def SearchLyric(artist, title):
	try:
	#if True:
		if len(artist) > 0:
			theurl = ("http://www.google.cn/search?hl=zh-CN&q=ti:" + title + "+ar:" + artist + "+filetype:lrc")
		else:
			theurl = ("http://www.google.cn/search?hl=zh-CN&q=ti:" + title + "+filetype:lrc")
		txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
		req = urllib2.Request(theurl, None, txheaders)
		# create a request object
		
		handle = urllib2.urlopen(req)
		html = handle.read()
		#print html
		sp = MySearchParser()
		sp.feed(html)
		return sp.dump()
	except:
		return ""

def DownLoadLyric(ID, artist, title):
	try:
		response = urllib2.urlopen(ID)
		return response.read()
	except:
		return ""

if __name__ == '__main__':
	print SearchLyric("羽泉", "深呼吸")
	#log.close()
		
		
	
