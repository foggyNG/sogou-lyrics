#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from gnomeosd import eventbridge

class DisplayOSD:
	def __init__(self):
		self.setting_ = {}
		# set default settings
		self.setting_['animation'] = 'off'
		self.setting_['vpos'] = 'top'
		self.setting_['halign'] = 'center'
		self.setting_['fgcolor'] = '#FFFF00'
		self.setting_['template'] = "<message id='RBLyrics' animations='%s' osd_fake_translucent_bg='off' drop_shadow='off' osd_vposition='%s' osd_halignment='%s'  hide_timeout='20000'><span size='20000' foreground='%s'>%s</span></message>"
		self.osd_ = eventbridge.OSD()
		return
		
	def show(self, message):
		xml = self.setting_['template'] % (
			self.setting_['animation'],
			self.setting_['vpos'],
			self.setting_['halign'],
			self.setting_['fgcolor'],
			message)
		self.osd_.send(xml)
		return
	
	def set(self, key, value):
		self.setting_[key] = value
		return
