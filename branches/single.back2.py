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

import logging, gtk, gtk.gdk, threading, gettext, pango, datetime, time, bisect, gobject

_ = gettext.gettext
log = logging.getLogger('RBLyrics')

## Gnome OSD displayer.
#
#  Display message using Gnome OSD interface.
class Single(gtk.Window, threading.Thread):
	
	## The constructor.
	#  @param prefs Preference.
	def __init__(self, shell, prefs):
		log.debug('enter')
		gtk.Window.__init__(self, gtk.WINDOW_POPUP)
		threading.Thread.__init__(self)
		#
		self._layout = self.create_pango_layout(_('RBLyrics'))
		self._layout.set_justify(False)
		self._layout.set_alignment(pango.ALIGN_LEFT)
		self._layout.set_ellipsize(pango.ELLIPSIZE_NONE)
		self._layout.set_width(pango.SCALE * (gtk.gdk.screen_width()-8))
		self._layout.set_font_description(pango.FontDescription(prefs.get('display.single.font')))
		#
		self._foreground = gtk.gdk.Color(prefs.get('display.single.foreground'))
		self._canvas = gtk.Image()
		self._canvas.show()
		self.add(self._canvas)
		self.add_events(gtk.gdk.POINTER_MOTION_HINT_MASK|gtk.gdk.BUTTON1_MOTION_MASK|gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK)
		self._move_base = None
		#self._canvas.window.set_cursor(gtk.gdk.FLEUR)
		self.connect('button-press-event', self._on_button_press)
		self.connect('button-release-event', self._on_button_release)
		self.connect('motion-notify-event', self._on_motion_notify)
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
		prefs.watcher.append(self)
		log.debug('leave')
		return
	
	def finialize(self):
		self._prefs.watcher.remove(self)
		self._runnable = False
		self.join()
		self.destroy()
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
		if name.startswith('display.single.'):
			if name == 'display.single.font':
				log.info(config)
				self._layout.set_font_description(pango.FontDescription(value))
			elif name == 'display.single.foreground':
				log.info(config)
				self._foreground = gtk.gdk.Color(prefs.get('display.single.foreground'))
			elif name == 'display.single.background':
				log.info(config)
				#self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(value))
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
			if line == self._lastline:
				continue
			self._lastline = line
			gtk.gdk.threads_enter()
			self.hide()
			gtk.gdk.threads_leave()
			try:
				log.error(line)
				self._layout.set_text(line)
				width, height = self._layout.get_pixel_size()
				foremap = gtk.gdk.Pixmap(None, width, height, 24)
				colormap = foremap.get_colormap()
				fgcolor = colormap.alloc_color(gtk.gdk.Color('#00FF00'))
				bgcolor = colormap.alloc_color(gtk.gdk.Color('#000000'))
				gc = gtk.gdk.GC(foremap)
				#gc.copy(self.style.fg_gc[gtk.STATE_NORMAL])
				gc.set_foreground(bgcolor)
				foremap.draw_rectangle(gc, True, 0, 0, width, height)
				foremap.draw_layout(gc, 0, 0, self._layout, fgcolor)
				#
				pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
				pixbuf.get_from_image(foremap.get_image(0,0,width,height), colormap, 0,0,0,0,width,height)
				log.error('%d %d %d' % (bgcolor.red, bgcolor.green, bgcolor.blue))
				newbuf = pixbuf.add_alpha(True, chr(bgcolor.red), chr(bgcolor.green), chr(bgcolor.blue))
				map, backmap = newbuf.render_pixmap_and_mask()
				del pixbuf, map
				log.info('step 1 finished')
			except Exception as e:
				log.error(e)
			gtk.gdk.threads_enter()
			try:
				self._canvas.set_from_pixmap(foremap, None)
				self.shape_combine_mask(backmap, 0, 0)
				del foremap, backmap
				width, height = self.get_size()
				log.info('%d, %d' % (width, height))
				#self.move(gtk.gdk.screen_width()/2-width/2, height)
				self.show()
			except Exception as e:
				log.error(e)
			finally:
				gtk.gdk.threads_leave()
		return
	
	def _on_button_press(self, widget, event):
		log.debug('enter')
		self._move_base = event.window.get_pointer()
		log.debug('leave')
		return True
	
	def _on_button_release(self, widget, event):
		log.debug('enter')
		self._move_base = event.window.get_pointer()
		log.info(event.window.get_position())
		log.debug('leave')
		return True
		
	def _on_motion_notify(self, widget, event):
		if event.is_hint:
			x, y, state = event.window.get_pointer()
			offset_x, offset_y = event.window.get_position()
			x = offset_x + x - self._move_base[0]
			y = offset_y + y - self._move_base[1]
			gtk.gdk.threads_enter()
			event.window.move(x,y)
			gtk.gdk.threads_leave()
		return True
		
