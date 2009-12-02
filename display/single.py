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


## @package RBLyrics.display.osd
#  Gnome OSD displayer.

import logging, gtk, threading, datetime, time, pango, bisect

log = logging.getLogger('RBLyrics')

## Gnome OSD displayer.
#
#  Display message using Gnome OSD interface.
class Single(gtk.Window, threading.Thread, object):
	
	## The constructor.
	#  @param prefs Preference.
	def __init__(self, shell, prefs):
		log.debug('enter')
		gtk.Window.__init__(self, gtk.WINDOW_POPUP)
		threading.Thread.__init__(self)
		#
		self._prefs = prefs
		self._running = False
		self._start_time = None
		self._lyrics = None
		self._timestamp = None
		self._lastline = None
		self._runnable = True
		self.start()
		#
		self._label = gtk.Label(_('RBLyrics'))
		self.add(self._label)
		self.set_font(prefs.get('display.single.font'))
		self.set_foreground(prefs.get('display.single.foreground'))
		self.set_background(prefs.get('display.single.background'))
		self.add_events(gtk.gdk.POINTER_MOTION_HINT_MASK|gtk.gdk.BUTTON1_MOTION_MASK|gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.ENTER_NOTIFY_MASK)
		self.connect('button-press-event', self._on_button_press)
		self.connect('motion-notify-event', self._on_motion)
		self.connect('enter-notify-event', self._on_enter)
		self.move(int(self._prefs.get('display.single.x')) - self.get_size()[0]/2, int(self._prefs.get('display.single.y')))
		self.show_all()
		log.debug('leave')
		return
	
	def finialize(self):
		log.debug('enter')
		self._runnable = False
		self.destroy()
		log.debug('leave')
		return
	
	def _on_button_press(self, widget, event):
		self._move_base = event.window.get_pointer()
		return False
		
	def _on_motion(self, widget, event):
		if event.is_hint:
			x, y, state = event.window.get_pointer()
			offset_x, offset_y = event.window.get_position()
			x = offset_x + x - self._move_base[0]
			y = offset_y + y - self._move_base[1]
			event.window.move(x,y)
		return True
	
	def _on_enter(self, widget, event):
		event.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.FLEUR))
		return True
		
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
	
	def synchronize(self, elapsed):
		self._start_time = datetime.datetime.now() - datetime.timedelta(seconds = elapsed)
		return
	
	def set_font(self, fontspec):
		self._label.modify_font(pango.FontDescription(fontspec))
		return
	
	def set_foreground(self, colorspec):
		self._label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(colorspec))
		return
	
	def set_background(self, colorspec):
		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(colorspec))
		return
	
	configer = property(lambda self : {
		'display.single.font' : self.set_font,
		'display.single.foreground' : self.set_foreground,
		'display.single.background' : self.set_background})

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
		
	def run(self):
		while(self._runnable):
			time.sleep(0.3)
			if (not self._running):
				continue
			#
			if self._lyrics is None:
				line = _('lyrics not found')
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
