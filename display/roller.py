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

import logging, gtk, gtk.gdk, gettext, pango, bisect

_ = gettext.gettext
log = logging.getLogger('RBLyrics')

class Roller(gtk.Window):
	
	def __init__(self, shell, prefs):
		log.debug('enter')
		gtk.Window.__init__(self)
		self.set_title(_('RBLyrics'))
		self.set_keep_above(True)
		self.stick()
		self.set_skip_taskbar_hint(True)
		self.connect('delete-event', self._on_delete)
		self.connect("configure-event", self._on_configure)
		self.set_default_size(int(prefs.get('display.roller.width')), int(prefs.get('display.roller.height')))
		self.move(int(prefs.get('display.roller.x')), int(prefs.get('display.roller.y')))
		self._layout = gtk.Layout()
		self._layout.add_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK|gtk.gdk.BUTTON1_MOTION_MASK|gtk.gdk.POINTER_MOTION_HINT_MASK)
		self._layout.connect("button-press-event", self._on_button_press)
		self._layout.connect("motion-notify-event", self._on_motion_notify)
		self._layout.connect("button-release-event", self._on_button_release)
		#
		self._font = pango.FontDescription(prefs.get('display.roller.font'))
		self._foreground = gtk.gdk.Color(prefs.get('display.roller.foreground'))
		bgcolor = gtk.gdk.Color(prefs.get('display.roller.background'))
		self._layout.modify_bg(gtk.STATE_NORMAL, bgcolor)
		self.modify_bg(gtk.STATE_NORMAL, bgcolor)
		#
		self._prefs = prefs
		self._running = False
		self._position_base = None
		self._drag_base = None
		self._lyrics = None
		self._lastline = None
		self._timestamp = None
		#
		self._scroll = 0
		self._vbox = gtk.VBox(True)
		line = gtk.Label(_('RBLyrics'))
		line.modify_fg(gtk.STATE_NORMAL, self._foreground)
		line.modify_font(self._font)
		self._vbox.pack_start(line)
		line.show()
		self._layout.put(self._vbox, 0, 0)
		self._lineheight = line.get_layout().get_pixel_size()[1]
		log.error(self._lineheight)
		container = gtk.HBox()
		container.pack_start(self._layout)
		container.show_all()
		self.add(container)
		self.show()
		self._layout.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
		self._prefs.watcher.append(self)
		log.debug('leave')
		return
		
	def _on_configure(self, widget, event):
		self._prefs.set('display.roller.x', str(event.x), False)
		self._prefs.set('display.roller.y', str(event.y), False)
		self._prefs.set('display.roller.width', str(event.width), False)
		self._prefs.set('display.roller.height', str(event.height), False)
		x = (event.width - self._vbox.size_request()[0])/2
		y = event.height /2
		self._layout.set_size(self._layout.allocation.width, self._vbox.size_request()[1] + event.height)
		self._layout.move(self._vbox, x, y)
		return
	
	def _on_delete(self, widget, response):
		self._prefs.set('display.roller', 'False')
		return
		
	def _on_button_press(self, widget, event):
		if event.button == 1:
			self._position_base = event.window.get_position()
			self._drag_base = (event.x_root, event.y_root)
			log.debug('drag %s' % str(self._drag_base))
		return True
		
	def _on_button_release(self, widget, event):
		if event.button == 1:
			self._position_base = None
			self._drag_base = None
			log.debug('drag finished')
		return True
		
	def _on_motion_notify(self, widget, event):
		if event.is_hint:
			log.debug('drag')
		else:
			log.debug('invalid')
		return True
		
	def finialize(self):
		self._prefs.watcher.remove(self)
		self.destroy()
		return

	def set_lyrics(self, lyrics):
		if lyrics != self._lyrics:
			self._lyrics = lyrics
			self._lastline = None
			if lyrics:
				self._timestamp = self._lyrics.content.keys()
				self._timestamp.sort()
				ptr = 0
				children = self._vbox.get_children()
				curcount = len(children)
				for t in self._timestamp:
					ptr += 1
					if curcount > ptr:
						children[ptr].set_text(self._lyrics.content[t])
					else:
						line = gtk.Label(self._lyrics.content[t])
						line.modify_fg(gtk.STATE_NORMAL, self._foreground)
						line.modify_font(self._font)
						self._vbox.pack_start(line)
						line.show()
				for l in range(ptr+1, curcount):
					children[l].hide()
				self.set_title('%s - %s' % (lyrics.ar, lyrics.ti))
				self._timestamp.insert(0, 0)
			else:
				children = self._vbox.get_children()
				curcount = len(children)
				for l in range(1, curcount):
					children[l].hide()
				self.set_title(_('RBLyrics'))
				self._timestamp = [0]
		return
	
	def resume(self):
		self._running = True
		return
	
	def pause(self):
		self._running = False
		return
	
	def synchronize(self, elapsed):
		if self._running:
			index = bisect.bisect_left(self._timestamp, elapsed)
			try:
				percent = float(elapsed - self._timestamp[index]) / float(self._timestamp[index+1] - self._timestamp[index])
				scroll =  int((index + percent) * self._lineheight)
				log.debug('%d %d %d' % (index, self._lineheight, scroll))
				self._layout.window.scroll(0, self._scroll - scroll)
				self._scroll = scroll
			except:
				pass
		
	def update_config(self, config):
		name = config.name
		value = config.value
		if name.startswith('display.roller.'):
			if name == 'display.roller.font':
				log.info(config)
				self._font = pango.FontDescription(value)
				children = self._vbox.get_children()
				for l in children:
					l.modify_font(self._font)
				self._lineheight = children[0].get_layout().get_pixel_size()[1]
			elif name == 'display.roller.foreground':
				log.info(config)
				self._foreground = gtk.gdk.Color(value)
				for l in self._children:
					l.modify_fg(gtk.STATE_NORMAL, self._foreground)
			elif name == 'display.roller.background':
				log.info(config)
				bgcolor = gtk.gdk.Color(value)
				self._layout.modify_bg(gtk.STATE_NORMAL, bgcolor)
				self.modify_bg(gtk.STATE_NORMAL, bgcolor)
		return
