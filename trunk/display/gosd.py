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
		self._osd = eventbridge.OSD()
		self._prefs = prefs
		self._running = False
		self._lyrics = [_('RBLyrics')]
		self._timestamp = [0, sys.maxint]
		self._lines = None
		self._lastline = None
		#
		self._animations = prefs.get('display.gosd.animations')
		self._avoid_panels = prefs.get('display.gosd.avoid_panels')
		self._drop_shadow = prefs.get('display.gosd.drop_shadow')
		self._hide_on_hover = prefs.get('display.gosd.hide_on_hover')
		self._font = prefs.get('display.gosd.font')
		self._color = prefs.get('display.gosd.color')
		self._vpos = prefs.get('display.gosd.vpos')
		self._halignment = prefs.get('display.gosd.halignment')
		prefs.watcher.append(self)
		return
	
	def finialize(self):
		self._prefs.watcher.remove(self)
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
				message = "<message id='RBLyrics' animations='%s' avoid_panels='%s' drop_shadow='%s' hide_on_hover='%s' osd_vposition='%s' osd_halignment='%s'><span font='%s' fgcolor='%s'>%s</span></message>" % (
					self._animations, self._avoid_panels, self._drop_shadow, self._hide_on_hover,
					self._vpos, self._halignment, self._font, self._color, line)
				self._osd.send(message)
		return
	
	def update_config(self, config):
		name = config.name
		value = config.value
		if name.startswith('display.gosd.'):
			log.info(config)
			if name == 'display.gosd.animations':
				self._animations = value
			elif name == 'display.gosd.avoid_panels':
				self._avoid_panels = value
			elif name == 'display.gosd.drop_shadow':
				self._drop_shadow = value
			elif name == 'display.gosd.hide_on_hover':
				self._hide_on_hover = value
			elif name == 'display.gosd.font':
				self._font = value
			elif name == 'display.gosd.color':
				self._color = value
			elif name == 'display.gosd.vpos':
				self._vpos = value
			elif name == 'display.gosd.halignment':
				self._halignment = value
		return
