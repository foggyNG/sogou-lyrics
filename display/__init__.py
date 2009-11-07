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

import logging

from RBLyrics.display.osd import OSD
log = logging.getLogger('RBLyrics')

## Lyrics displayer manager.
class Display:
	
	## @var _interface
	#  Display interface.
	
	## The constructor.
	#  @param prefs Preference.
	def __init__(self, prefs):
		log.debug('enter')
		self._interface = OSD(prefs)
		log.debug('leave')
		return
	
	## Display message.
	#  @param message Message to show.
	def show(self, message):
		self._interface.show(message)
		return
		
