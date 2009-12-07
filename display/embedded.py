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

import rb
import logging, gtk, gtk.gdk, gettext, pango, bisect, sys

_ = gettext.gettext
log = logging.getLogger('RBLyrics')

class Embedded(gtk.EventBox):
	
	def __init__(self, shell, prefs):
		gtk.EventBox.__init__(self)
		#
		self._prefs = prefs
		self._running = False
		self._lyrics = None
		self._timestamp = [0, sys.maxint]
		self._lines = [_('RBLyrics')]
		self._lastline = None
		#
		self._shell = shell
		self._label = gtk.Label(_('RBLyrics'))
		self._label.modify_font(pango.FontDescription(prefs.get('display.embedded.font')))
		self._label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(prefs.get('display.embedded.foreground')))
		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(prefs.get('display.embedded.background')))
		self.add(self._label)
		self._shell.add_widget(self, rb.SHELL_UI_LOCATION_MAIN_TOP)
		self.show_all()
		#
		prefs.watcher.append(self)
		return
	
	def finialize(self):
		self._prefs.watcher.remove(self)
		self._shell.remove_widget(self, rb.SHELL_UI_LOCATION_MAIN_TOP)
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
				self._label.set_text(line)
		return
	
	def update_config(self, config):
		name = config.name
		value = config.value
		if name.startswith('display.embedded.'):
			log.info(config)
			if name == 'display.embedded.font':
				self._label.modify_font(pango.FontDescription(value))
			elif name == 'display.embedded.foreground':
				self._label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(value))
			elif name == 'display.embedded.background':
				self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(value))
		return
