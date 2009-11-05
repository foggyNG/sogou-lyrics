#!/usr/bin/env python
#-*- coding: UTF-8 -*-

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

from gnomeosd import eventbridge

from RBLyrics.utils import log

## Gnome OSD displayer.
#
#  Display message using Gnome OSD interface.
class OSD:
	
	## @var _prefs
	#  Preference.
	
	## @var _template
	#  Message template.
	
	## @var _osd
	#  OSD object.
	
	## The constructor.
	#  @param prefs Preference.
	def __init__(self, prefs):
		log.debug('enter')
		self._prefs = prefs
		self._template = "<message id='RBLyrics' animations='%s' osd_fake_translucent_bg='off' drop_shadow='off' osd_vposition='%s' osd_halignment='%s'  hide_timeout='20000'><span size='20000' foreground='%s'>%s</span></message>"
		self._osd = eventbridge.OSD()
		log.debug('leave')
		return
	
	## Display message.
	#  @param message Message to show.
	def show(self, message):
		if self._prefs.get('display'):
			xml = self._template % (
				self._prefs.get('animation'),
				self._prefs.get('vpos'),
				self._prefs.get('halign'),
				self._prefs.get('fgcolor'),
				message)
			self._osd.send(xml)
		return
		
