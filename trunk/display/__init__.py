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
#  歌词显示模块。

import logging
from embedded import Embedded
from gosd import GOSD
from roller import Roller
from single import Single
log = logging.getLogger('RBLyrics')

## 歌词显示引擎。
display_map = {
	'display.single' : Single,
	'display.roller' : Roller,
	'display.gosd' : GOSD,
	'display.embedded' : Embedded
}

## 歌词显示模块管理器。
class Display:
	
	## 构造函数。
	#  @param shell RBShell。
	#  @param prefs 选项管理器。
	def __init__(self, shell, prefs):
		self._shell = shell
		self._prefs = prefs
		prefs.watcher.append(self)
		self._interface = {}
		for config in prefs.setting.values():
			self.update_config(config)
		return
	
	## 继续。
	def resume(self):
		for e in self._interface.values():
			e.resume()
		return
	
	## 暂停。
	def pause(self):
		for e in self._interface.values():
			e.pause()
		return
	
	## 设置歌词。
	#  @param lyrics 歌词信息。
	def set_lyrics(self, lyrics):
		for e in self._interface.values():
			e.set_lyrics(lyrics)
		return
	
	## 同步。
	#  @param elapsed 播放时间。
	def synchronize(self, elapsed):
		for e in self._interface.values():
			e.synchronize(elapsed)
		return
	
	## 销毁。
	def finialize(self):
		for e in self._interface.values():
			e.finialize()
		self._prefs.watcher.remove(self)
		return
	
	## 更新配置。
	#  @param config 待更新的配置项。
	def update_config(self, config):
		name = config.name
		value = config.value
		if name.startswith('display.') and len(name.split('.')) == 2:
			log.info(config)
			if not display_map.has_key(name):
				log.error('invalid display mode : %s' % name)
			elif (name in self._interface) and value == 'False':
				e = self._interface.pop(name)
				e.finialize()
			elif (not name in self._interface) and value == 'True':
				self._interface[name] = display_map[name](self._shell, self._prefs)
		return
		
