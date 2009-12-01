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

## @package RBLyrics.display
#  Displayer.

import logging, gtk, gtk.gdk, pango

from singleline import SingleLine
from doubleline import DoubleLine
log = logging.getLogger('RBLyrics')

## Lyrics displayer manager.
class Display(gtk.Window):
	
	## @var _interface
	#  Display interface.
	
	## The constructor.
	#  @param prefs Preference.
	def __init__(self, prefs):
		gtk.Window.__init__(self, gtk.WINDOW_POPUP)
		self.set_gravity(gtk.gdk.GRAVITY_CENTER)
		log.debug('enter')
		if self.is_composited():
			self.set_opacity(0.5)
		self._interface = SingleLine(prefs, self)
		self.add(self._interface)
		self._interface.show_all()
		#
		self.add_events(gtk.gdk.POINTER_MOTION_HINT_MASK|gtk.gdk.BUTTON1_MOTION_MASK|gtk.gdk.BUTTON_PRESS_MASK)
		self.connect('button-press-event', self._on_button_press)
		self.connect('motion-notify-event', self._on_motion)
		
		#self.show()
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
		
	def interface(self):
		return self._interface
			
		
