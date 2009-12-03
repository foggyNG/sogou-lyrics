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

import logging, gtk, threading, datetime, time, pango, os
from utils import get_seconds, get_position

log = logging.getLogger('RBLyrics')

## Gnome OSD displayer.
#
#  Display message using Gnome OSD interface.
class DoubleLine(gtk.DrawingArea, threading.Thread):
	
	## @var _prefs
	#  Preference.
	
	## @var _template
	#  Message template.
	
	## @var _osd
	#  OSD object.
	
	## The constructor.
	#  @param prefs Preference.
	def __init__(self, prefs, window):
		gtk.DrawingArea.__init__(self)
		threading.Thread.__init__(self)
		self.set_size_request(200,50)
		log.debug('enter')
		#
		self._layout = self.create_pango_layout('')
		self._layout.set_justify(False)
		self._layout.set_alignment(pango.ALIGN_CENTER)
		self._layout.set_font_description(pango.FontDescription(prefs.get('display.font')))
		self._layout.set_ellipsize(pango.ELLIPSIZE_NONE)
		self._layout.set_width(pango.SCALE * (gtk.gdk.screen_width()-8))
		#
		self._window = window
		self._prefs = prefs
		self._running = False
		self._start_time = None
		self._lyrics = None
		self._timestamp = None
		self._pos = -1
		self._trigger = 0
		self._runnable = True
		self._lastpos = -1
		self.start()
		log.debug('leave')
		return
	
	## Display message.
	#  @param message Message to show.
	def run(self):
		while(self._runnable):
			time.sleep(0.3)
			if (not self._running):
				continue
			#
			if self._lyrics is None:
				text = _('lyrics not found!')
			else:
				now = datetime.datetime.now()
				elapsed = get_seconds(now - self._start_time)
				past, found = get_position(self._timestamp, elapsed)
				if past == self._lastpos:
					continue
				self._lastpos = past
				if past<0:
					linepast = ''
				else:
					linepast = self._lyrics.get_line(self._timestamp[past])
				if past + 1 >= len(self._timestamp):
					linenow = ''
				else:
					linenow = self._lyrics.get_line(self._timestamp[past+1])
				if self._trigger % 2 == 0:
					text = linenow + os.linesep + linepast
				else:
					text = linepast + os.linesep + linenow
				self._trigger += 1
			gtk.gdk.threads_enter()
			x, y = self._window.get_position()
			log.error(text)
			self._layout.set_markup(text)
			width, height = self._layout.get_pixel_size()
			width += 4
			height += 4
			off_x = (width - gtk.gdk.screen_width())/2 + 2
			off_y = 2
			self.set_size_request(width, height)
			self.realize()
			fgcolor = self.get_colormap().alloc_color(self._prefs.get('display.color'))
			bgcolor = self.get_colormap().alloc_color('#000')
			pixmap = gtk.gdk.Pixmap(self.window, width, height)
			fg_gc = gtk.gdk.GC(pixmap); fg_gc.copy(self.style.fg_gc[gtk.STATE_NORMAL])
			bg_gc = gtk.gdk.GC(pixmap); bg_gc.copy(self.style.fg_gc[gtk.STATE_NORMAL])
			fg_gc.set_foreground(fgcolor)
			bg_gc.set_background(bgcolor)
			pixmap.draw_rectangle(bg_gc, True, 0, 0, width, height)
			pixmap.draw_layout(fg_gc, off_x, off_y, self._layout)
			self.window.set_back_pixmap(pixmap, False)
			#
			#pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
			#pixbuf.get_from_drawable(self.window, self.window.get_colormap(), 0, 0, 0, 0, width, height)
			#pixmap, bitmap = pixbuf.render_pixmap_and_mask(255)
			bitmap = gtk.gdk.Pixmap(self.window, width, height, 1)
			fg_gc = gtk.gdk.GC(bitmap)
			bg_gc = gtk.gdk.GC(bitmap)
			fg_gc.set_foreground(gtk.gdk.Color(pixel=-1))
			bg_gc.set_background(gtk.gdk.Color(pixel=0))
			bitmap.draw_rectangle(bg_gc, True, 0, 0, width, height)
			bitmap.draw_layout(fg_gc, off_x, off_y, self._layout)
			bitmap.draw_layout(fg_gc, off_x + 1, off_y, self._layout)
			bitmap.draw_layout(fg_gc, off_x + 1, off_y + 1, self._layout)
			bitmap.draw_layout(fg_gc, off_x, off_y + 1, self._layout)
			bitmap.draw_layout(fg_gc, off_x - 1, off_y + 1, self._layout)
			bitmap.draw_layout(fg_gc, off_x - 1, off_y, self._layout)
			bitmap.draw_layout(fg_gc, off_x - 1, off_y - 1, self._layout)
			bitmap.draw_layout(fg_gc, off_x, off_y - 1, self._layout)
			bitmap.draw_layout(fg_gc, off_x + 1, off_y - 1, self._layout)
			
			self._window.window.shape_combine_mask(bitmap, 0, 0)
			
			#self._window.width = width
			#self._window.height = height
			self._window.move(x, y)
			gtk.gdk.threads_leave()
		return
	
	def resume(self):
		log.debug('enter')
		self._start_time = datetime.datetime.now()
		self._running = True
		log.debug('leave')
		return
		
	def pause(self):
		log.debug('enter')
		self._running = False
		log.debug('leave')
		return
		
	def synchronize(self, elapsed):
		self._start_time = datetime.datetime.now() - datetime.timedelta(seconds = elapsed)
		return
	
	def set_lyrics(self, lyrics):
		log.debug('enter')
		self._lyrics = lyrics
		self._pos = -1
		if lyrics:
			self._timestamp = lyrics.get_content().keys()
			self._timestamp.sort()
		log.debug('leave')
		return
