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
import rb
import os, gtk, gconf, logging, urllib, gettext, pango, gtk.gdk
from engine import engine_map
from utils import LRC_PATH_TEMPLATE
_ = gettext.gettext
log = logging.getLogger('RBLyrics')

class Config(object):
	
	def __init__(self, name, key, default, readonly):
		self._name = name
		self._key = key
		self._default = default
		self._readonly = readonly
		try:
			self._value = gconf.client_get_default().get_without_default(self._key).get_string()
		except :
			self._value = default
		log.info(self)
		return
		
	def _set_value(self, value):
		self._value = value
		gconf.client_get_default().set_string(self._key, value)
		return
		
	def __str__(self):
		return 'Config %s = %s' % (self._name, self._value)
		
	name = property(lambda self : self._name)
	key = property(lambda self : self._key)
	default = property(lambda self : self._default)
	value = property(lambda self : self._value, _set_value)
	readonly = property(lambda self : self._readonly)

## Application preference.
#
#  Parse and retrieve application preferece, display preference dialog.
class Preference(gtk.Dialog, object):
	
	## The constructor.
	def __init__(self):
		log.debug('enter')
		gtk.Dialog.__init__(self, title = _('Preferences'), flags = gtk.DIALOG_NO_SEPARATOR)
		self._setting = {}
		for name in engine_map.keys():
			self._setting[name] = Config(name, '/apps/rhythmbox/plugins/RBLyrics/%s' % name, 'True', False)
		self._setting['display.embedded'] = Config('display.embedded', '/apps/rhythmbox/plugins/RBLyrics/display.embedded', 'True', False)
		self._setting['display.embedded.font'] = Config('display.embedded.font', '/apps/rhythmbox/plugins/RBLyrics/display.embedded.font', '13', False)
		self._setting['display.embedded.foreground'] = Config('display.embedded.foreground', '/apps/rhythmbox/plugins/RBLyrics/display.embedded.foreground', '#FF0080', False)
		self._setting['display.embedded.background'] = Config('display.embedded.background', '/apps/rhythmbox/plugins/RBLyrics/display.embedded.background', '#EDECEB', False)
		self._setting['display.single'] = Config('display.single', '/apps/rhythmbox/plugins/RBLyrics/display.single', 'True', False)
		self._setting['display.single.x'] = Config('display.single.x', '/apps/rhythmbox/plugins/RBLyrics/display.single.x', str(gtk.gdk.screen_width()/2), True)
		self._setting['display.single.y'] = Config('display.single.y', '/apps/rhythmbox/plugins/RBLyrics/display.single.y', 40, True)
		self._setting['display.single.font'] = Config('display.single.font', '/apps/rhythmbox/plugins/RBLyrics/display.single.font', '18', False)
		self._setting['display.single.foreground'] = Config('display.single.foreground', '/apps/rhythmbox/plugins/RBLyrics/display.single.foreground', '#00FF40', False)
		self._setting['display.single.background'] = Config('display.single.background', '/apps/rhythmbox/plugins/RBLyrics/display.single.background', '#000000', False)
		self._setting['display.double'] = Config('display.double', '/apps/rhythmbox/plugins/RBLyrics/display.double', 'True', True)
		self._setting['display.double.x'] = Config('display.double.x', '/apps/rhythmbox/plugins/RBLyrics/display.double.x', str(gtk.gdk.screen_width()/2), True)
		self._setting['display.double.y'] = Config('display.double.y', '/apps/rhythmbox/plugins/RBLyrics/display.double.y', 30, True)
		self._setting['display.double.font'] = Config('display.double.font', '/apps/rhythmbox/plugins/RBLyrics/display.double.font', '18', True)
		self._setting['display.double.foreground'] = Config('display.double.foreground', '/apps/rhythmbox/plugins/RBLyrics/display.double.foreground', '#FFFF00', True)
		self._setting['display.double.background'] = Config('display.double.background', '/apps/rhythmbox/plugins/RBLyrics/display.double.background', '#000000', True)
		self._setting['display.roller'] = Config('display.roller', '/apps/rhythmbox/plugins/RBLyrics/display.roller', 'True', True)
		self._setting['display.roller.x'] = Config('display.roller.x', '/apps/rhythmbox/plugins/RBLyrics/display.roller.x', str(gtk.gdk.screen_width()/2), True)
		self._setting['display.roller.y'] = Config('display.roller.y', '/apps/rhythmbox/plugins/RBLyrics/display.roller.y', 30, True)
		self._setting['display.roller.width'] = Config('display.roller.width', '/apps/rhythmbox/plugins/RBLyrics/display.roller.width', str(gtk.gdk.screen_width()/2), True)
		self._setting['display.roller.height'] = Config('display.roller.height', '/apps/rhythmbox/plugins/RBLyrics/display.roller.height', 30, True)
		self._setting['display.roller.font'] = Config('display.roller.font', '/apps/rhythmbox/plugins/RBLyrics/display.roller.font', '18', True)
		self._setting['display.roller.foreground'] = Config('display.roller.foreground', '/apps/rhythmbox/plugins/RBLyrics/display.roller.foreground', '#FFFF00', True)
		self._setting['display.roller.background'] = Config('display.roller.background', '/apps/rhythmbox/plugins/RBLyrics/display.roller.background', '#000000', True)
		self._setting['main.download'] = Config('main.download', '/apps/rhythmbox/plugins/RBLyrics/main.download', 'True', False)
		self._setting['main.directory'] = Config('main.directory', '/apps/rhythmbox/plugins/RBLyrics/main.directory', os.path.join(rb.user_cache_dir(), 'lyrics'), False)
		self._setting['main.file_pattern'] = Config('main.file_pattern', '/apps/rhythmbox/plugins/RBLyrics/main.file_pattern', LRC_PATH_TEMPLATE[0], False)
		# init dialog widgets
		self.connect('delete-event', self._on_delete_event)
		self.set_default_size(640, 480)
		self._model = gtk.ListStore(str, str, str, str, int, str)
		names = self._setting.keys()
		names.sort()
		for n in names:
			c = self._setting[n]
			if c.value != c.default:
				weight = pango.WEIGHT_BOLD
			else:
				weight = pango.WEIGHT_NORMAL
			if c.readonly:
				color = '#EDECEB'
			else:
				color = '#000000'
			self._model.append([c.name, _(c.name), c.value, _(c.value), weight, color])
		#
		treeview = gtk.TreeView(self._model)
		treeview.set_rules_hint(True)
		cell = gtk.CellRendererText()
		vc = gtk.TreeViewColumn(_('Name'), cell, text = 1, weight = 4, foreground = 5)
		vc.set_sort_column_id(0)
		treeview.append_column(vc)
		vc = gtk.TreeViewColumn(_('Value'), cell, text = 3, weight = 4, foreground = 5)
		treeview.append_column(vc)
		treeview.connect('row-activated', self._on_row_activated)
		scroll = gtk.ScrolledWindow()
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll.add_with_viewport(treeview)
		self.get_content_area().add(scroll)
		self.get_content_area().show_all()
		#
		btnlog = gtk.Button(_('Log'))
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
		btnlog.set_image(icon)
		btnlog.connect('released', self._on_btnlog_released)
		self.get_action_area().pack_end(btnlog, False, False)
		#
		btnrestore = gtk.Button(_('Restore'))
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
		btnrestore.set_image(icon)
		btnrestore.connect('released', self._on_btnrestore_released)
		self.get_action_area().pack_end(btnrestore, False, False)
		#
		btnclose = gtk.Button(_('Close'))
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_BUTTON)
		btnclose.set_image(icon)
		btnclose.connect('released', self._on_btnclose_released)
		self.get_action_area().pack_end(btnclose, False, False)
		self.get_action_area().show_all()
		#
		self._watcher = []
		log.debug('leave')
		return
	
	def _on_delete_event(self, widget, event):
		widget.hide()
		return True
	
	def _on_btnrestore_released(self, widget):
		log.debug('enter')
		iter = self._model.get_iter_first()
		while iter != None:
			name = self._model.get_value(iter, 0)
			c = self._setting[name]
			# TODO remove readonly assertion
			if not c.readonly and c.value != c.default:
				c.value = c.default
				self._model.set_value(iter, 2, c.value)
				self._model.set_value(iter, 3, _(c.value))
				self._model.set_value(iter, 4, pango.WEIGHT_NORMAL)
				log.info(c)
				for w in self._watcher:
					w.update_config(c)
			iter = self._model.iter_next(iter)
		log.debug('leave')
		return
		
	def _on_row_activated(self, treeview, path, column):
		log.debug('enter <%s>' % path)
		iter = self._model.get_iter(path)
		name = self._model.get_value(iter, 0)
		c = self._setting[name]
		if not c.readonly:
			value = None
			if c.name in ['engine.sogou', 'engine.minilyrics', 'engine.lyricist', 'engine.ttplayer',
				'display.embedded', 'display.single',
				'main.download']:
				value = str(c.value != 'True')
			elif c.name in ['display.embedded.foreground', 'display.embedded.background',
				'display.single.foreground', 'display.single.background']:
				dialog = gtk.ColorSelectionDialog(_('Choose color'))
				dialog.get_color_selection().set_current_color(gtk.gdk.color_parse(c.value))
				response = dialog.run()
				dialog.hide()
				if response == gtk.RESPONSE_OK:
					value = dialog.get_color_selection().get_current_color().to_string()
				dialog.destroy()
			elif c.name in ['display.embedded.font', 'display.single.font']:
				dialog = gtk.FontSelectionDialog(_('Choose font'))
				dialog.set_font_name(c.value)
				response = dialog.run()
				dialog.hide()
				if response == gtk.RESPONSE_OK:
					value = dialog.get_font_name()
				dialog.destroy()
			elif c.name == 'main.directory':
				dialog = gtk.FileChooserDialog(title = _('Select lyrics folder'), action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
				filter = gtk.FileFilter()
				filter.add_mime_type('inode/directory')
				dialog.set_filter(filter)
				dialog.set_current_folder(c.value)
				response = dialog.run()
				dialog.hide()
				if response == gtk.RESPONSE_OK:
					value = dialog.get_filename()
				dialog.destroy()
			elif c.name == 'main.file_pattern':
				dialog = gtk.Dialog(_('Lyrics save pattern'), self, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
				model = gtk.ListStore(str, str)
				combo = gtk.ComboBox(model)
				cell = gtk.CellRendererText()
				combo.pack_start(cell)
				combo.add_attribute(cell, 'text', 0)
				for k in LRC_PATH_TEMPLATE:
					choice = model.append([_(k), k])
					if k == c.value:
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
					value = model.get_value(choice, 1)
				dialog.destroy()
			# update view
			if value != None and value != c.value:
				c.value = value
				self._model.set_value(iter, 2, c.value)
				self._model.set_value(iter, 3, _(c.value))
				if c.value != c.default:
					weight = pango.WEIGHT_BOLD
				else:
					weight = pango.WEIGHT_NORMAL
				self._model.set_value(iter, 4, weight)
				log.info(c)
				for w in self._watcher:
					w.update_config(c)
		log.debug('leave')
		return
		
	def _on_btnlog_released(self, widget):
		path = rb.find_user_cache_file('RBLyrics/log')
		log.info('open <file://%s>' % urllib.pathname2url(path))
		os.system('/usr/bin/xdg-open \"%s\"' % path)
		return
	
	def _on_btnclose_released(self, widget):
		self.hide()
		return
	
	def get(self, name):
		return self._setting[name].value
		
	def get_engine(self):
		engine = []
		for k in self._setting.keys():
			if k.startswith('engine.'):
				v = self._setting[k]
				if v.value == 'True':
					engine.append(k)
		return engine

	setting = property(lambda self : self._setting)
	watcher = property(lambda self : self._watcher)
