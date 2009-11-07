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

## @package RBLyrics.prefs
#  Preference.

import os, gtk, gconf, logging
from gtk.gdk import color_parse
from gtk.glade import XML

from RBLyrics.engine import engine_map
log = logging.getLogger('RBLyrics')

## Gconf settings.
#  Application settings are stored in Gconf.
gconf_keys = {
'display' : '/apps/rhythmbox/plugins/RBLyrics/display',
'download' : '/apps/rhythmbox/plugins/RBLyrics/download',
'halign' : '/apps/rhythmbox/plugins/RBLyrics/halign',
'vpos' : '/apps/rhythmbox/plugins/RBLyrics/vpos',
'fgcolor' : '/apps/rhythmbox/plugins/RBLyrics/fgcolor',
'font' : '/apps/rhythmbox/plugins/RBLyrics/font',
'folder' : '/apps/rhythmbox/plugins/RBLyrics/folder',
'engine' : '/apps/rhythmbox/plugins/RBLyrics/engine',
'choose' : '/apps/rhythmbox/plugins/RBLyrics/choose'
}

halign_map = {
0 : 'left',
1 : 'center',
2 : 'right'
}

vpos_map = {
0 : 'top',
1 : 'center',
2 : 'bottom'
}

## Application preference.
#
#  Parse and retrieve application preferece, display preference dialog.
class Preference:
	
	## @var _gconf
	#  Gconf handler.
	
	## @var _dialog
	#  Preference dialog object.
	
	## @var _widget
	#  Widgets in preference dialog.
	
	## @var _setting
	#  Preference settings.
	
	## The constructor.
	#  @param glade_file Input glade file for preference dialog.
	def __init__(self, glade_file):
		log.debug('enter')
		# get main dialog frome glade file
		self._gconf = gconf.client_get_default()
		gladexml = XML(glade_file)
		self._dialog = gladexml.get_widget('prefs')
		self._dialog.connect('response', self._dialog_response)
		# get widgets from glade file
		self._widget = {}
		for key in ['display','download','halign','vpos','fgcolor','font','folder', 'choose'] + engine_map.keys():
			self._widget[key] = gladexml.get_widget(key)
		filter = gtk.FileFilter()
		filter.add_mime_type('inode/directory')
		self._widget['folder'].set_filter(filter)
		# load settings
		self._setting = {}
		self._load_prefs()
		log.debug('leave')
		return
	
	## Response handler for the dialog.
	def _dialog_response(self, dialog, response):
		dialog.hide()
		return
	
	## Set 'display' setting.
	def _set_display(self, widget):
		key = 'display'
		value = widget.get_active()
		self._setting[key] = value
		self._gconf.set_bool(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
		return
	
	## Set 'download' setting.
	def _set_download(self, widget):
		key = 'download'
		value = widget.get_active()
		self._setting[key] = value
		self._gconf.set_bool(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
		return
	
	## Set 'choose' setting.
	def _set_choose(self, widget):
		key = 'choose'
		value = widget.get_active()
		self._setting[key] = value
		self._gconf.set_bool(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
		return
	
	## Set 'halign' setting.
	def _set_halign(self, widget):
		key = 'halign'
		value = widget.get_active()
		self._setting[key] = halign_map[value]
		self._gconf.set_int(gconf_keys[key], value)
		log.info('%s : %s' % (key, halign_map[value]))
		return
	
	## Set 'vpos' setting.
	def _set_vpos(self, widget):
		key = 'vpos'
		value = widget.get_active()
		self._setting[key] = vpos_map[value]
		self._gconf.set_int(gconf_keys[key], value)
		log.info('%s : %s' % (key, vpos_map[value]))
		return
	
	## Set 'fgcolor' setting.
	def _set_fgcolor(self, widget):
		key = 'fgcolor'
		value = widget.get_color().to_string()
		self._setting[key] = value
		self._gconf.set_string(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
		return
	
	## Set 'font' setting.
	def _set_font(self, widget):
		key = 'font'
		value = widget.get_font_name()
		self._setting[key] = value
		self._gconf.set_string(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
		return
	
	## Set 'folder' setting.
	def _set_folder(self, widget):
		key = 'folder'
		value = widget.get_filename()
		self._setting[key] = value
		self._gconf.set_string(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
		return
	
	## Set 'engine' setting.
	def _set_engine(self, widget):
		key = 'engine'
		widget_key = widget.get_name()
		value = self._setting[key]
		if widget.get_active() and not widget_key in value:
			value.append(widget_key)
		elif not widget.get_active() and widget_key in value:
			value.remove(widget_key)
		self._setting[key] = value
		self._gconf.set_list(gconf_keys[key], gconf.VALUE_STRING, value)
		log.info('%s : %s' % (key, value))
		return
	
	## Get preference dialog.
	#  @return Dialog object.
	def get_dialog (self):
		return self._dialog
	
	## Get setting.
	#  @param key Key of the setting.
	#  @return Value to the key.
	def get(self, key):
		return self._setting[key]
	
	
	## Load preference from Gconf.
	# @bug pygtk bug
	def _load_prefs (self):
		log.debug('enter')
		# display
		key = 'display'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_bool()
		except:
			value = True
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_active(value)
		widget.connect('toggled', self._set_display)
		# download
		key = 'download'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_bool()
		except:
			value = True
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_active(value)
		widget.connect('toggled', self._set_download)
		# choose
		key = 'choose'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_bool()
		except:
			value = True
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_active(value)
		widget.connect('toggled', self._set_choose)
		# halign
		key = 'halign'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_int()
		except:
			value = 1
		self._setting[key] = halign_map[value]
		log.info('%s : %s' % (key, halign_map[value]))
		widget.set_active(value)
		widget.connect('changed', self._set_halign)
		# vpos
		key = 'vpos'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_int()
		except:
			value = 0
		self._setting[key] = vpos_map[value]
		log.info('%s : %s' % (key, vpos_map[value]))
		widget.set_active(value)
		widget.connect('changed', self._set_vpos)
		# font
		key = 'font'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_string()
		except:
			value = '20'
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_font_name(value)
		widget.connect('font-set', self._set_font)
		# fgcolor
		key = 'fgcolor'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_string()
			color_parse(value)
		except:
			value = '#FFFF00'
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_color(color_parse(value))
		widget.connect('color-set', self._set_fgcolor)
		# folder
		key = 'folder'
		widget = self._widget[key]
		try:
			value = self._gconf.get_without_default(gconf_keys[key]).get_string()
		except:
			value = os.path.expanduser('~/.lyrics')
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_filename(value)
		widget.connect('file-set', self._set_folder)
		# @bug pygtk bug
		# widget.connect('selection-changed', self.set_folder)
		# engine
		key = 'engine'
		try:
			value = []
			temp = self._gconf.get_without_default(gconf_keys[key]).get_list()
			for t in temp:
				value.append(t.get_string())
		except:
			value = engine_map.keys()
		self._setting[key] = []
		for k in value:
			if k in engine_map.keys():
				self._setting[key].append(k)
		log.info('%s : %s' % (key, self._setting[key]))
		for engine in engine_map.keys():
			self._widget[engine].set_active(engine in value)
			self._widget[engine].connect('toggled', self._set_engine)
		log.debug('leave')
		return
