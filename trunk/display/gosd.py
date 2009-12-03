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

import logging, gettext, bisect
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
			if lyrics:
				self._timestamp = self._lyrics.content.keys()
				self._timestamp.sort()
		return
	
	def _get_line(self, elapsed):
		index = bisect.bisect_left(self._timestamp, elapsed)
		if index == len(self._timestamp):
			# over the last line
			line = self._lyrics.content[self._timestamp[index-1]]
		elif elapsed == self._timestamp[index]:
			# found the line
			line = self._lyrics.content[elapsed]
		elif index > 0:
			# using the previous line
			line = self._lyrics.content[self._timestamp[index-1]]
		else:
			line = _('RBLyrics')
		return line
		
	def synchronize(self, elapsed):
		if self._running:
			if self._lyrics is None:
				line = _('Lyrics not found')
			else:
				line = self._get_line(elapsed)
			if line != self._lastline:
				self._lastline = line
				self._osd.send('<message>%s</message>' % line)
		return
