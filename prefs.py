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

## @package RBLyrics.prefs
#  Preference.

import os, gtk, gconf
from gtk.gdk import color_parse
from gtk.glade import XML

from RBLyrics.utils import log
from RBLyrics.engine import engine_map

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
'engine' : '/apps/rhythmbox/plugins/RBLyrics/engine'
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
		for key in ['display','download','halign','vpos','fgcolor','font','folder'] + engine_map.keys():
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
	
	## Set 'halign' setting.
	def _set_halign(self, widget):
		key = 'halign'
		value = widget.get_active_text()
		self._setting[key] = value
		self._gconf.set_string(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
		return
	
	## Set 'vpos' setting.
	def _set_vpos(self, widget):
		key = 'vpos'
		value = widget.get_active_text()
		self._setting[key] = value
		self._gconf.set_string(gconf_keys[key], value)
		log.info('%s : %s' % (key, value))
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
	def _load_prefs (self):
		log.debug('enter')
		# display
		key = 'display'
		value = None
		widget = self._widget[key]
		try:
			value = self._gconf.get_bool(gconf_keys[key])
		except:
			value = True
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_active(value)
		widget.connect('toggled', self._set_display)
		# download
		key = 'download'
		value = None
		widget = self._widget[key]
		try:
			value = self._gconf.get_bool(gconf_keys[key])
		except:
			value = True
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_active(value)
		widget.connect('toggled', self._set_download)
		# halign
		key = 'halign'
		value = None
		widget = self._widget[key]
		model = widget.get_model()
		index = 0
		try:
			value = self._gconf.get_string(gconf_keys[key])
			iter = model.get_iter_first()
			found = False
			while iter:
				if model.get_value(iter,0) == value:
					found = True
					break
				else:
					index += 1
					iter = model.iter_next(iter)
			if not found :
				index = 0
				value = model.get_value(model.get_iter_first(), 0)
		except:
			index = 0
			value = model.get_value(model.get_iter_first(), 0)
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_active(index)
		widget.connect('changed', self._set_halign)
		# vpos
		key = 'vpos'
		value = None
		widget = self._widget[key]
		model = widget.get_model()
		index = 0
		try:
			value = self._gconf.get_string(gconf_keys[key])
			iter = model.get_iter_first()
			found = False
			while iter:
				if model.get_value(iter,0) == value:
					found = True
					break
				else:
					index += 1
					iter = model.iter_next(iter)
			if not found :
				index = 0
				value = model.get_value(model.get_iter_first(), 0)
		except:
			index = 0
			value = model.get_value(model.get_iter_first(), 0)
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_active(index)
		widget.connect('changed', self._set_vpos)
		# font
		key = 'font'
		value = None
		widget = self._widget[key]
		try:
			value = self._gconf.get_string(gconf_keys[key])
			if value is None:
				value = 'Sans Italic 20'
		except:
			value = 'Sans Italic 20'
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_font_name(value)
		widget.connect('font-set', self._set_font)
		# fgcolor
		key = 'fgcolor'
		value = None
		widget = self._widget[key]
		try:
			value = self._gconf.get_string(gconf_keys[key])
			color_parse(value)
		except:
			value = '#FFFF00'
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_color(color_parse(value))
		widget.connect('color-set', self._set_fgcolor)
		# folder
		key = 'folder'
		value = None
		widget = self._widget[key]
		try:
			value = self._gconf.get_string(gconf_keys[key])
			if not value:
				value = os.path.expanduser('~/.lyrics')
		except:
			value = os.path.expanduser('~/.lyrics')
		self._setting[key] = value
		log.info('%s : %s' % (key, value))
		widget.set_filename(value)
		widget.connect('file-set', self._set_folder)
		# pygtk bug
		# widget.connect('selection-changed', self.set_folder)
		# engine
		key = 'engine'
		value = None
		try:
			value = self._gconf.get_list(gconf_keys[key], gconf.VALUE_STRING)
			if value is None:
				value = engine_map.keys()
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
