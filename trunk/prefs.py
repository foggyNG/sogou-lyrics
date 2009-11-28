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

import os, gtk, gconf, logging, urllib, rb, gettext, pango, gtk.gdk
from engine import engine_map
from utils import LRC_PATH_TEMPLATE
_ = gettext.gettext
log = logging.getLogger('RBLyrics')

class Config:
	
	def __init__(self, name, key, default):
		self._name = name
		self._key = key
		self._default = default
		try:
			self._value = gconf.client_get_default().get_without_default(self._key).get_string()
		except :
			self._value = default
		log.info(self)
		return
	
	def set_value(self, value):
		self._value = value
		gconf.client_get_default().set_string(self._key, value)
		return
	
	def default(self):
		return self._default
		
	def value(self):
		return self._value
		
	def name(self):
		return self._name
		
	def __str__(self):
		return '<Config %s = %s>' % (self._name, self._value)

## Application preference.
#
#  Parse and retrieve application preferece, display preference dialog.
class Preference:
	
	## @var _dialog
	#  Preference dialog object.
	
	## @var _setting
	#  Preference settings.
	
	## The constructor.
	def __init__(self):
		log.debug('enter')
		self._setting = {}
		self._setting['engine.sogou'] = Config('engine.sogou', '/apps/rhythmbox/plugins/RBLyrics/engine.sogou', 'True')
		self._setting['engine.lyricist'] = Config('engine.lyricist', '/apps/rhythmbox/plugins/RBLyrics/engine.lyricist', 'True')
		self._setting['engine.minilyrics'] = Config('engine.minilyrics', '/apps/rhythmbox/plugins/RBLyrics/engine.minilyrics', 'True')
		self._setting['engine.ttplayer'] = Config('engine.ttplayer', '/apps/rhythmbox/plugins/RBLyrics/engine.ttplayer', 'True')
		self._setting['display.horizontal'] = Config('display.horizontal', '/apps/rhythmbox/plugins/RBLyrics/display.horizontal', 'center')
		self._setting['display.vertical'] = Config('display.vertical', '/apps/rhythmbox/plugins/RBLyrics/display.vertical', 'top')
		self._setting['main.display'] = Config('main.display', '/apps/rhythmbox/plugins/RBLyrics/main.display', 'True')
		self._setting['main.download'] = Config('main.download', '/apps/rhythmbox/plugins/RBLyrics/main.download', 'True')
		self._setting['main.directory'] = Config('main.directory', '/apps/rhythmbox/plugins/RBLyrics/main.directory', os.path.join(rb.user_cache_dir(), 'lyrics'))
		self._setting['display.font'] = Config('display.font', '/apps/rhythmbox/plugins/RBLyrics/display.font', '20')
		self._setting['display.color'] = Config('display.color', '/apps/rhythmbox/plugins/RBLyrics/display.color', '#FFFF00')
		self._setting['display.hide_on_hover'] = Config('display.hide_on_hover', '/apps/rhythmbox/plugins/RBLyrics/display.hide_on_hover', 'True')
		self._setting['display.animations'] = Config('display.animations', '/apps/rhythmbox/plugins/RBLyrics/display.animations', 'False')
		self._setting['display.avoid_panels'] = Config('display.avoid_panels', '/apps/rhythmbox/plugins/RBLyrics/display.avoid_panels', 'True')
		self._setting['main.file_pattern'] = Config('main.file_pattern', '/apps/rhythmbox/plugins/RBLyrics/main.file_pattern', LRC_PATH_TEMPLATE[0])
		# init dialog widgets
		self._dialog = gtk.Dialog(title = _('Preferences'), flags = gtk.DIALOG_NO_SEPARATOR)
		self._dialog.connect('delete-event', self._on_delete_event)
		self._dialog.set_default_size(400, 350)
		self._model = gtk.ListStore(str, str, int, str, str)
		names = self._setting.keys()
		names.sort()
		for n in names:
			c = self._setting[n]
			if c.value() != c.default():
				weight = pango.WEIGHT_BOLD
			else:
				weight = pango.WEIGHT_NORMAL
			self._model.append([c.name(), c.value(), weight, _(c.name()), _(c.value())])
		#
		treeview = gtk.TreeView(self._model)
		treeview.set_rules_hint(True)
		cell = gtk.CellRendererText()
		vc = gtk.TreeViewColumn(_('Name'), cell, text = 3, weight = 2)
		vc.set_sort_column_id(0)
		treeview.append_column(vc)
		vc = gtk.TreeViewColumn(_('Value'), cell, text = 4, weight = 2)
		treeview.append_column(vc)
		treeview.connect('row-activated', self._on_row_activated)
		scroll = gtk.ScrolledWindow()
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll.add_with_viewport(treeview)
		self._dialog.get_content_area().add(scroll)
		self._dialog.get_content_area().show_all()
		#
		btnlog = gtk.Button(_('Log'))
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
		btnlog.set_image(icon)
		btnlog.connect('released', self._on_btnlog_released)
		self._dialog.get_action_area().pack_end(btnlog, False, False)
		#
		btnrestore = gtk.Button(_('Restore'))
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
		btnrestore.set_image(icon)
		btnrestore.connect('released', self._on_btnrestore_released)
		self._dialog.get_action_area().pack_end(btnrestore, False, False)
		#
		btnclose = gtk.Button(_('Close'))
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_BUTTON)
		btnclose.set_image(icon)
		btnclose.connect('released', self._on_btnclose_released)
		self._dialog.get_action_area().pack_end(btnclose, False, False)
		self._dialog.get_action_area().show_all()
		log.debug('leave')
		return
	
	def _on_delete_event(self, widget, event):
		log.debug('enter')
		widget.hide()
		log.debug('leave')
		return True
	
	def _on_btnrestore_released(self, widget):
		log.debug('enter')
		iter = self._model.get_iter_first()
		while iter != None:
			name = self._model.get_value(iter, 0)
			c = self._setting[name]
			c.set_value(c.default())
			self._model.set_value(iter, 1, c.value())
			self._model.set_value(iter, 2, pango.WEIGHT_NORMAL)
			self._model.set_value(iter, 4, _(c.value()))
			log.info(c)
			iter = self._model.iter_next(iter)
		log.debug('leave')
		return
		
	def _on_row_activated(self, treeview, path, column):
		log.debug('enter <%s>' % path)
		iter = self._model.get_iter(path)
		name = self._model.get_value(iter, 0)
		c = self._setting[name]
		if c.name() in ['engine.sogou', 'engine.minilyrics', 'engine.lyricist', 'engine.ttplayer', 
		'main.display', 'main.download', 'display.hide_on_hover', 'display.animations', 'display.avoid_panels']:
			c.set_value(str(c.value() != 'True'))
		elif c.name() == 'display.color':
			dialog = gtk.ColorSelectionDialog(_('Choose foreground color'))
			dialog.get_color_selection().set_current_color(gtk.gdk.color_parse(c.value()))
			response = dialog.run()
			dialog.hide()
			if response == gtk.RESPONSE_OK:
				c.set_value(dialog.get_color_selection().get_current_color().to_string())
		elif c.name() == 'display.font':
			dialog = gtk.FontSelectionDialog(_('Choose font'))
			dialog.set_font_name(c.value())
			response = dialog.run()
			dialog.hide()
			if response == gtk.RESPONSE_OK:
				c.set_value(dialog.get_font_name())
		elif c.name() == 'main.directory':
			dialog = gtk.FileChooserDialog(title = _('Select lyrics folder'), action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
			filter = gtk.FileFilter()
			filter.add_mime_type('inode/directory')
			dialog.set_filter(filter)
			dialog.set_current_folder(c.value())
			response = dialog.run()
			dialog.hide()
			if response == gtk.RESPONSE_OK:
				c.set_value(dialog.get_filename())
		elif c.name() == 'display.horizontal':
			dialog = gtk.Dialog(_('Horizontal'), self._dialog, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
			model = gtk.ListStore(str, str)
			combo = gtk.ComboBox(model)
			cell = gtk.CellRendererText()
			combo.pack_start(cell)
			combo.add_attribute(cell, 'text', 0)
			for k in ['left', 'center', 'right']:
				choice = model.append([_(k), k])
				if k == c.value():
					combo.set_active_iter(choice)
			container = gtk.HBox()
			dialog.get_content_area().pack_start(container, False, False, 10)
			container.pack_start(gtk.Label(_('Horizontal')), False, False, 10)
			container.pack_start(combo, False, False, 10)
			dialog.show_all()
			response = dialog.run()
			dialog.hide()
			if response == gtk.RESPONSE_OK:
				choice = combo.get_active_iter()
				c.set_value(model.get_value(choice, 1))
		elif c.name() == 'display.vertical':
			dialog = gtk.Dialog(_('Vertical'), self._dialog, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
			model = gtk.ListStore(str, str)
			combo = gtk.ComboBox(model)
			cell = gtk.CellRendererText()
			combo.pack_start(cell)
			combo.add_attribute(cell, 'text', 0)
			for k in ['top', 'center', 'bottom']:
				choice = model.append([_(k), k])
				if k == c.value():
					combo.set_active_iter(choice)
			container = gtk.HBox()
			dialog.get_content_area().pack_start(container, False, False, 10)
			container.pack_start(gtk.Label(_('Vertical')), False, False, 10)
			container.pack_start(combo, False, False, 10)
			dialog.show_all()
			response = dialog.run()
			dialog.hide()
			if response == gtk.RESPONSE_OK:
				choice = combo.get_active_iter()
				c.set_value(model.get_value(choice, 1))
		elif c.name() == 'main.file_pattern':
			dialog = gtk.Dialog(_('Lyrics save pattern'), self._dialog, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
			model = gtk.ListStore(str, str)
			combo = gtk.ComboBox(model)
			cell = gtk.CellRendererText()
			combo.pack_start(cell)
			combo.add_attribute(cell, 'text', 0)
			for k in LRC_PATH_TEMPLATE:
				choice = model.append([_(k), k])
				if k == c.value():
					combo.set_active_iter(choice)
			container = gtk.HBox()
			dialog.get_content_area().pack_start(container, False, False, 10)
			container.pack_start(gtk.Label(_('Lyrics save pattern')), False, False, 10)
			container.pack_start(combo, False, False, 10)
			dialog.show_all()
			response = dialog.run()
			dialog.hide()
			if response == gtk.RESPONSE_OK:
				choice = combo.get_active_iter()
				c.set_value(model.get_value(choice, 1))
		# update view
		self._model.set_value(iter, 1, c.value())
		self._model.set_value(iter, 4, _(c.value()))
		if c.value() != c.default():
			weight = pango.WEIGHT_BOLD
		else:
			weight = pango.WEIGHT_NORMAL
		self._model.set_value(iter, 2, weight)
		log.info(c)
		log.debug('leave')
		return
		
	def _on_btnlog_released(self, widget):
		log.debug('enter')
		path = rb.find_user_cache_file('RBLyrics/log')
		log.info('open <file://%s>' % urllib.pathname2url(path))
		os.system('/usr/bin/xdg-open \"%s\"' % path)
		log.debug('leave')
		return
	
	def _on_btnclose_released(self, widget):
		log.debug('enter')
		self._dialog.hide()
		log.debug('leave')
		return
	
	## Get preference dialog.
	#  @return Dialog object.
	def get_dialog (self):
		return self._dialog
	
	## Get setting.
	#  @param key Key of the setting.
	#  @return Value to the key.
	def get(self, key):
		return self._setting[key].value()
	
	def get_engine(self):
		engine = []
		if self._setting['engine.sogou'].value() == 'True':
			engine.append('sogou')
		if self._setting['engine.lyricist'].value() == 'True':
			engine.append('lyricist')
		if self._setting['engine.minilyrics'].value() == 'True':
			engine.append('minilyrics')
		if self._setting['engine.ttplayer'].value() == 'True':
			engine.append('ttplayer')
		return engine

