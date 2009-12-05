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


## @package RBLyrics.display.embedded
#  Embedded displayer.

import logging, gettext, bisect, sys
from gnomeosd import eventbridge

_ = gettext.gettext
log = logging.getLogger('RBLyrics')

class GOSD:
	
	def __init__(self, shell, prefs):
		log.debug('enter')
		self._osd = eventbridge.OSD()
		self._running = False
		self._lyrics = None
		self._timestamp = None
		self._lines = None
		self._lastline = None
		log.debug('leave')
		return
	
	def finialize(self):
		del self._osd
		return
		
	def resume(self):
		self._running = True
		return
	
	def pause(self):
		self._running = False
		return
	
	def set_lyrics(self, lyrics):
		if lyrics != self._lyrics:
			self._lyrics = lyrics
			self._lastline = None
			self._lines = [_('RBLyrics')]
			if lyrics:
				content = self._lyrics.content
				self._timestamp = content.keys()
				self._timestamp.sort()
				for t in self._timestamp:
					self._lines.append(content[t])
				self._timestamp.insert(0, 0)
				self._timestamp.append(sys.maxint)
			else:
				self._timestamp = [0, sys.maxint]
		return
	
	def _get_line(self, elapsed):
		index = bisect.bisect_right(self._timestamp, elapsed)
		line = self._lines[index-1]
		return line
		
	def synchronize(self, elapsed):
		if self._running:
			line = self._get_line(elapsed)
			if line != self._lastline:
				self._lastline = line
				self._osd.send('<message>%s</message>' % line)
		return
