#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from gnomeosd import eventbridge

class DisplayOSD:
	def __init__(self, prefs):
		self.__prefs = prefs
		self.__template = "<message id='RBLyrics' animations='%s' osd_fake_translucent_bg='off' drop_shadow='off' osd_vposition='%s' osd_halignment='%s'  hide_timeout='20000'><span size='20000' foreground='%s'>%s</span></message>"
		self.__osd = eventbridge.OSD()
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
		
