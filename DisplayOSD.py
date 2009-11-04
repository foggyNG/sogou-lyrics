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

from gnomeosd import eventbridge

from utils import log

class DisplayOSD:
	def __init__(self, prefs):
		log.debug('enter')
		self.__prefs = prefs
		self.__template = "<message id='RBLyrics' animations='%s' osd_fake_translucent_bg='off' drop_shadow='off' osd_vposition='%s' osd_halignment='%s'  hide_timeout='20000'><span size='20000' foreground='%s'>%s</span></message>"
		self.__osd = eventbridge.OSD()
		log.debug('leave')
		return
		
	def show(self, message):
		if self.__prefs.get('display'):
			xml = self.__template % (
				self.__prefs.get('animation'),
				self.__prefs.get('vpos'),
				self.__prefs.get('halign'),
				self.__prefs.get('fgcolor'),
				message)
			self.__osd.send(xml)
		return
		
