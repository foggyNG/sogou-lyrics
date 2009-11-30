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

import logging, gtk, threading, datetime, time, pango
from utils import get_seconds

log = logging.getLogger('RBLyrics')

## Gnome OSD displayer.
#
#  Display message using Gnome OSD interface.
class Single(gtk.DrawingArea, threading.Thread):
	
	## @var _prefs
	#  Preference.
	
	## @var _template
	#  Message template.
	
	## @var _osd
	#  OSD object.
	
	## The constructor.
	#  @param prefs Preference.
	def __init__(self, prefs):
		gtk.DrawingArea.__init__(self)
		threading.Thread.__init__(self)
		log.debug('enter')
		#
		self._prefs = prefs
		self._running = False
		self._start_time = None
		self._lyrics = None
		self._runnable = True
		self._lastline = None
		log.debug('leave')
		self.start()
		return
	
	## Display message.
	#  @param message Message to show.
	def run(self):
		while(self._runnable):
			time.sleep(0.3)
			if (not self._running) or (self._lyrics is None):
				continue
			#
			now = datetime.datetime.now()
			elapsed = get_seconds(now - self._start_time)
			line = self._lyrics.get_line(elapsed)
			if line is None or line == self._lastline:
				continue
			self._lastline = line
			log.error(line)
			layout = self.create_pango_layout(line)
			layout.set_ellipsize(pango.ELLIPSIZE_NONE)
			layout.set_justify(False)
			layout.set_alignment(pango.ALIGN_CENTER)
			layout.set_font_description(pango.FontDescription(self._prefs.get('display.font')))
			layout.set_width(pango.SCALE * gtk.gdk.screen_width())
			width, height = layout.get_pixel_size()
			log.error(layout.get_pixel_extents())
			log.error(layout.get_pixel_size())
			off_x = (width - gtk.gdk.screen_width())/2
			self.set_size_request(width, height)
			self.realize()
			pixmap = gtk.gdk.Pixmap(self.window, width, height)
			fg_gc = gtk.gdk.GC(pixmap)
			bg_gc = gtk.gdk.GC(pixmap)
			fg_gc.set_foreground(gtk.gdk.Color(self._prefs.get('display.color')))
			bg_gc.set_background(gtk.gdk.Color('#000000'))
			pixmap.draw_rectangle(bg_gc, True, 0, 0, width, height)
			pixmap.draw_layout(fg_gc, off_x, 0, layout)
			bitmap = gtk.gdk.Pixmap(self.window, width, height, 1)
			fg_gc = gtk.gdk.GC(bitmap)
			bg_gc = gtk.gdk.GC(bitmap)
			fg_gc.set_foreground(gtk.gdk.Color(self._prefs.get('display.color')))
			bg_gc.set_background(gtk.gdk.Color('#000000'))

			
			bitmap.draw_rectangle(bg_gc, True, 0, 0, width, height)
			bitmap.draw_layout(fg_gc, off_x, 0, layout)
			BORDER_WIDTH = 1
			bitmap.draw_layout(fg_gc, off_x + BORDER_WIDTH, 0, layout)
			bitmap.draw_layout(fg_gc, off_x + BORDER_WIDTH, 0 + BORDER_WIDTH, layout)
			bitmap.draw_layout(fg_gc, off_x, 0 + BORDER_WIDTH, layout)
			bitmap.draw_layout(fg_gc, off_x - BORDER_WIDTH, 0 + BORDER_WIDTH, layout)
			bitmap.draw_layout(fg_gc, off_x - BORDER_WIDTH, 0, layout)
			bitmap.draw_layout(fg_gc, off_x - BORDER_WIDTH, 0 - BORDER_WIDTH, layout)
			bitmap.draw_layout(fg_gc, off_x, 0 - BORDER_WIDTH, layout)
			bitmap.draw_layout(fg_gc, off_x + BORDER_WIDTH, 0 - BORDER_WIDTH, layout)
			self.window.set_back_pixmap(pixmap, False)
			self.window.shape_combine_mask(bitmap, 0, 0)
		return
	
	def resume(self):
		self._start_time = datetime.datetime.now()
		self._running = True
		return
		
	def pause(self):
		self._running = False
		return
		
	def synchronize(self, elapsed):
		self._start_time = datetime.datetime.now() - datetime.timedelta(seconds = elapsed)
		return
	
	def set_lyrics(self, lyrics):
		self._lyrics = lyrics
		return
