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
import logging, gtk, gtk.gdk, threading, gettext, pango, datetime, time, bisect

_ = gettext.gettext
log = logging.getLogger('RBLyrics')

class Embedded(gtk.EventBox, threading.Thread):
	
	def __init__(self, shell, prefs):
		log.debug('enter')
		gtk.EventBox.__init__(self)
		threading.Thread.__init__(self)
		#
		self._prefs = prefs
		self._runnable = True
		self._running = False
		self._start_time = datetime.datetime.now()
		self._lyrics = None
		self._timestamp = None
		self._lastline = None
		self.start()
		#
		self._shell = shell
		self._label = gtk.Label(_('RBLyrics'))
		self._label.modify_font(pango.FontDescription(prefs.get('display.embedded.font')))
		self._label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(prefs.get('display.embedded.foreground')))
		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(prefs.get('display.embedded.background')))
		self.add(self._label)
		gtk.gdk.threads_enter()
		self._shell.add_widget(self, rb.SHELL_UI_LOCATION_MAIN_TOP)
		self.show_all()
		gtk.gdk.threads_leave()
		#
		prefs.watcher.append(self)
		log.debug('leave')
		return
	
	def finialize(self):
		self._prefs.watcher.remove(self)
		self._runnable = False
		self.join()
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
		self._start_time = datetime.datetime.now() - datetime.timedelta(seconds = elapsed)
		return
	
	def update_config(self, config):
		log.debug('enter %s' % config)
		name = config.name
		value = config.value
		if name.startswith('display.embedded.'):
			if name == 'display.embedded.font':
				log.info(config)
				self._label.modify_font(pango.FontDescription(value))
			elif name == 'display.embedded.foreground':
				log.info(config)
				self._label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(value))
			elif name == 'display.embedded.background':
				log.info(config)
				self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(value))
		log.debug('leave')
		return

	def run(self):
		while(self._runnable):
			time.sleep(0.3)
			if not self._running:
				continue
			#
			if self._lyrics is None:
				line = _('Lyrics not found')
			else:
				timedelta = datetime.datetime.now() - self._start_time
				elapsed = timedelta.days * 24 * 3600 + timedelta.seconds + int(timedelta.microseconds >= 500000)
				line = self._get_line(elapsed)
			if line != self._lastline:
				self._lastline = line
				gtk.gdk.threads_enter()
				self._label.set_text(line)
				gtk.gdk.threads_leave()
		return