#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#
#	   
#	   Copyright 2009 wonder <gogo.wonder@gmail.com>
#	   
#	   This program is free software; you can redistribute it and/or modify
#	   it under the terms of the GNU General Public License as published by
#	   the Free Software Foundation; either version 2 of the License, or
#	   (at your option) any later version.
#	   
#	   This program is distributed in the hope that it will be useful,
#	   but WITHOUT ANY WARRANTY; without even the implied warranty of
#	   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	   GNU General Public License for more details.
#	   
#	   You should have received a copy of the GNU General Public License
#	   along with this program; if not, write to the Free Software
#	   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	   MA 02110-1301, USA.


## @package RBLyrics.display.single
#  水平滚动显示模式。

import logging, gtk, gtk.gdk, gettext, pango, bisect, sys, datetime, gobject

_ = gettext.gettext
log = logging.getLogger('RBLyrics')

SPACING = 10

## 水平滚动显示模式。
class Single(gtk.Window):
	
	## 构造函数。
	#  @param shell RBShell。
	#  @param prefs 选项管理器。
	def __init__(self, shell, prefs):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
		#
		self._shell = shell
		self._prefs = prefs
		self._running = False
		self._drag_base = None
		self._start_time = datetime.datetime.now()
		self._lyrics = None
		self._timestamp = [0, sys.maxint]
		self._firstline = gtk.Label(_('RBLyrics'))
		self._lastline = self._firstline
		self._update_source = None
		self._scroll = 0
		self._font = pango.FontDescription(prefs.get('display.single.font'))
		self._varfont = self._font.copy()
		self._varfont.set_weight(pango.WEIGHT_BOLD)
		self._foreground = gtk.gdk.Color(prefs.get('display.single.foreground'))
		self._highlight = gtk.gdk.Color(prefs.get('display.single.highlight'))
		#
		self._firstline.modify_fg(gtk.STATE_NORMAL, self._highlight)
		self._firstline.modify_font(self._font)
		self._hbox = gtk.HBox(False, SPACING)
		self._hbox.pack_start(self._firstline)
		self._layout = gtk.Layout()
		bgcolor = gtk.gdk.Color(prefs.get('display.single.background'))
		self._layout.modify_bg(gtk.STATE_NORMAL, bgcolor)
		self._layout.put(self._hbox, 0, 0)
		container = gtk.HBox()
		container.pack_start(self._layout)
		container.show_all()
		self.add(container)
		self.modify_bg(gtk.STATE_NORMAL, bgcolor)
		self.set_decorated(False)
		self.set_keep_above(True)
		self.stick()
		self.set_skip_taskbar_hint(True)
		self.set_opacity(float(prefs.get('display.single.opacity'))/100)
		x,y,w,h = map(int, prefs.get('display.single.window').split(','))
		self._layout.realize()
		self.realize()
		self.set_default_size(w, self._hbox.size_request()[1])
		self.move(x, y)
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
		self._prefs.watcher.append(self)
		self.connect('configure-event', self._on_configure)
		self.connect('button-press-event', self._on_button_press)
		return
	
	def _on_configure(self, widget, event):
		self._layout.set_size(self._hbox.size_request()[0] + event.width, self._layout.allocation.height)
		self._layout.move(self._hbox, event.width/2, 0)
		self._prefs.set('display.single.window', '%d,%d,%d,%d' % (event.x,event.y,event.width,event.height), False)
		return False
		
	def _on_button_press(self, widget, event):
		catched = False
		if event.button == 3:
			widget.begin_resize_drag(gtk.gdk.WINDOW_EDGE_EAST, event.button, int(event.x_root), int(event.y_root), event.time)
			catched = True
		elif event.button == 1:
			widget.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
			catched = True
		return catched
	
	## 销毁。	
	def finialize(self):
		self._prefs.watcher.remove(self)
		if self._update_source and not gobject.source_remove(self._update_source):
			log.warn('update source remove failed %d' % self._update_source)
		self._update_source = None
		self.destroy()
		return
	
	## 设置歌词。
	#  @param lyrics 歌词信息。
	def set_lyrics(self, lyrics):
		if lyrics != self._lyrics:
			self._lyrics = lyrics
			self._lastline.modify_fg(gtk.STATE_NORMAL, self._foreground)
			self._lastline = self._firstline
			self._lastline.modify_fg(gtk.STATE_NORMAL, self._highlight)
			if lyrics:
				content = self._lyrics.content
				self._timestamp = content.keys()
				self._timestamp.sort()
				ptr = 0
				children = self._hbox.get_children()
				curcount = len(children)
				for t in self._timestamp:
					ptr += 1
					if curcount > ptr:
						children[ptr].set_text(content[t])
					else:
						line = gtk.Label(content[t])
						line.modify_fg(gtk.STATE_NORMAL, self._foreground)
						line.modify_font(self._font)
						self._hbox.pack_start(line)
				for line in children[ptr+1:]:
					line.set_text('')
				self._timestamp.insert(0, 0)
				self._timestamp.append(sys.maxint)
			else:
				children = self._hbox.get_children()
				for line in children[1:]:
					line.set_text('')
				self._timestamp = [0, sys.maxint]
			for line in self._hbox.get_children():
				line.show()
			event = gtk.gdk.Event(gtk.gdk.CONFIGURE)
			event.x, event.y = self.get_position()
			event.width, event.height = self.get_size()
			self.emit('configure-event', event)
			self._layout.window.scroll(self._scroll, 0)
			self._scroll = 0
		return
	
	## 继续。
	def resume(self):
		if not self._running:
			self._running = True
			if not self._update_source:
				self._update_source = gobject.timeout_add(100, self._scroll_left)
			self.present()
			x,y,w,h = map(int, self._prefs.get('display.single.window').split(','))
			self.move(x, y)
		return
	
	## 暂停。
	def pause(self):
		if self._running:
			self._running = False
			if self._update_source and not gobject.source_remove(self._update_source):
				log.warn('update source remove failed %d' % self._update_source)
			self._update_source = None
			self.hide()
		return
	
	def _scroll_left(self):
		if self._running:
			elapsed = datetime.datetime.now() - self._start_time
			seconds = self._get_milli(elapsed) / 1000
			index = bisect.bisect_right(self._timestamp, seconds) - 1
			line = self._hbox.get_children()[index]
			if line != self._lastline:
				self._lastline.modify_fg(gtk.STATE_NORMAL, self._foreground)
				line.modify_fg(gtk.STATE_NORMAL, self._highlight)
				self._lastline = line
			line_elapsed = self._get_milli(elapsed) - self._timestamp[index] * 1000
			line_duration = 1000 * (self._timestamp[index+1] - self._timestamp[index])
			score = float(line_elapsed) / line_duration
			children = self._hbox.get_children()
			scroll = int(score * children[index].allocation.width)
			for c in children[:index]:
				scroll += c.allocation.width + SPACING
			self._layout.window.scroll(self._scroll - scroll, 0)
			self._scroll = scroll
		return self._running
	
	def _get_milli(self, delta):
		return delta.days * 24 * 3600 * 1000 + delta.seconds * 1000 + delta.microseconds / 1000
	
	## 同步。
	#  @param elapsed 播放时间。
	def synchronize(self, elapsed):
		start_new = datetime.datetime.now() - datetime.timedelta(seconds = elapsed)
		milli = self._get_milli(start_new - self._start_time)
		if abs(milli) > 500:
			self._start_time = start_new
		return
	
	## 更新配置。
	#  @param config 待更新的配置项。
	def update_config(self, config):
		name = config.name
		value = config.value
		if name.startswith('display.single.'):
			log.info(config)
			if name == 'display.single.font':
				self._font = pango.FontDescription(value)
				children = self._hbox.get_children()
				for l in children:
					l.modify_font(self._font)
				self.resize(self.allocation.width, self._hbox.size_request()[1])
			elif name == 'display.single.foreground':
				self._foreground = gtk.gdk.Color(value)
				for l in self._hbox.get_children():
					l.modify_fg(gtk.STATE_NORMAL, self._foreground)
			elif name == 'display.single.highlight':
				self._highlight = gtk.gdk.Color(value)
				self._lastline.modify_fg(gtk.STATE_NORMAL, self._highlight)
			elif name == 'display.single.background':
				bgcolor = gtk.gdk.Color(value)
				self._layout.modify_bg(gtk.STATE_NORMAL, bgcolor)
				self.modify_bg(gtk.STATE_NORMAL, bgcolor)
			elif name == 'display.single.opacity':
				self.set_opacity(float(self._prefs.get('display.single.opacity'))/100)
		return
