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
from gnomeosd import capplet
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

COMBO_PRESET = {'main.file_pattern' : LRC_PATH_TEMPLATE}
class ComboDialog(gtk.Dialog):
	
	def __init__(self):
		gtk.Dialog.__init__(self, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		self._model = gtk.ListStore(str, str)
		self._combo = gtk.ComboBox(self._model)
		cell = gtk.CellRendererText()
		self._combo.pack_start(cell)
		self._combo.add_attribute(cell, 'text', 1)
		container = gtk.HBox()
		self.get_content_area().pack_start(container, False, False, 10)
		self._label = gtk.Label()
		container.pack_start(self._label, False, False, 10)
		container.pack_start(self._combo, False, False, 10)
		container.show_all()
		return
	
	def set_preset(self, preset):
		gtk.Dialog.set_title(self, _(preset))
		self._label.set_text(_(preset))
		self._model.clear()
		for c in COMBO_PRESET[preset]:
			self._model.append([c, _(c)])
		return
		
	def get_selection(self):
		choice = self._combo.get_active_iter()
		value = self._model.get_value(choice, 0)
		return value
	
	def set_selection(self, value):
		iter = self._model.get_iter_first()
		while iter:
			if self._model.get_value(iter, 0) == value:
				self._combo.set_active_iter(iter)
				break
			iter = self._model.iter_next(iter)
		return
		
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
		self._setting['display.gosd'] = Config('display.gosd', '/apps/rhythmbox/plugins/RBLyrics/display.gosd', 'True', False)
		self._setting['display.embedded'] = Config('display.embedded', '/apps/rhythmbox/plugins/RBLyrics/display.embedded', 'True', False)
		self._setting['display.embedded.font'] = Config('display.embedded.font', '/apps/rhythmbox/plugins/RBLyrics/display.embedded.font', '13', False)
		self._setting['display.embedded.foreground'] = Config('display.embedded.foreground', '/apps/rhythmbox/plugins/RBLyrics/display.embedded.foreground', '#FF0080', False)
		self._setting['display.embedded.background'] = Config('display.embedded.background', '/apps/rhythmbox/plugins/RBLyrics/display.embedded.background', '#EDECEB', False)
		self._setting['display.roller'] = Config('display.roller', '/apps/rhythmbox/plugins/RBLyrics/display.roller', 'True', True)
		self._setting['display.roller.x'] = Config('display.roller.x', '/apps/rhythmbox/plugins/RBLyrics/display.roller.x', '0', True)
		self._setting['display.roller.y'] = Config('display.roller.y', '/apps/rhythmbox/plugins/RBLyrics/display.roller.y', '20', True)
		self._setting['display.roller.width'] = Config('display.roller.width', '/apps/rhythmbox/plugins/RBLyrics/display.roller.width', str(int(gtk.gdk.screen_width()/3)), True)
		self._setting['display.roller.height'] = Config('display.roller.height', '/apps/rhythmbox/plugins/RBLyrics/display.roller.height', str(int(gtk.gdk.screen_height()/3)), True)
		self._setting['display.roller.font'] = Config('display.roller.font', '/apps/rhythmbox/plugins/RBLyrics/display.roller.font', '18', True)
		self._setting['display.roller.foreground'] = Config('display.roller.foreground', '/apps/rhythmbox/plugins/RBLyrics/display.roller.foreground', '#FF0080', True)
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
				color = '#A9A9A9'
			else:
				color = '#000000'
			self._model.append([c.name, _(c.name), c.value, _(c.value), weight, color])
		#
		treeview = gtk.TreeView(self._model)
		treeview.set_rules_hint(True)
		cell = gtk.CellRendererText()
		vc = gtk.TreeViewColumn(_('Name'), cell, text = 1, weight = 4)
		vc.set_sort_column_id(0)
		treeview.append_column(vc)
		cell = gtk.CellRendererText()
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
		self._dlgcolor = None
		self._dlgfont = None
		self._dlgdirectory = None
		self._dlgcombo = None
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
			if c.value != c.default:
				self._on_value_changed(c, iter, c.default)
			iter = self._model.iter_next(iter)
		log.debug('leave')
		return
		
	def _on_value_changed(self, c, iter, value, watch = True):
		c.value = value
		self._model.set_value(iter, 2, c.value)
		self._model.set_value(iter, 3, _(c.value))
		if c.value != c.default:
			weight = pango.WEIGHT_BOLD
		else:
			weight = pango.WEIGHT_NORMAL
		self._model.set_value(iter, 4, weight)
		log.debug(c)
		if watch:
			for w in self._watcher:
				w.update_config(c)
		return
		
	def _on_bool_set(self, c, iter):
		value = str(c.value != 'True')
		self._on_value_changed(c, iter, value)
		return
	
	def _on_color_set(self, c, iter):
		if not self._dlgcolor:
			self._dlgcolor = gtk.ColorSelectionDialog('')
		self._dlgcolor.set_title(_(c.name))
		self._dlgcolor.get_color_selection().set_current_color(gtk.gdk.color_parse(c.value))
		response = self._dlgcolor.run()
		self._dlgcolor.hide()
		if response == gtk.RESPONSE_OK:
			value = self._dlgcolor.get_color_selection().get_current_color().to_string()
			self._on_value_changed(c, iter, value)
		return
	
	def _on_font_set(self, c, iter):
		if not self._dlgfont:
			self._dlgfont = gtk.FontSelectionDialog(_('Choose font'))
		self._dlgfont.set_title(_(c.name))
		self._dlgfont.set_font_name(c.value)
		response = self._dlgfont.run()
		self._dlgfont.hide()
		if response == gtk.RESPONSE_OK:
			value = self._dlgfont.get_font_name()
			self._on_value_changed(c, iter, value)
		return
		
	def _on_directory_set(self, c, iter):
		if not self._dlgdirectory:
			self._dlgdirectory = gtk.FileChooserDialog(action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
			filter = gtk.FileFilter()
			filter.add_mime_type('inode/directory')
			self._dlgdirectory.set_filter(filter)
		self._dlgdirectory.set_title(_(c.name))
		self._dlgdirectory.set_current_folder(c.value)
		response = self._dlgdirectory.run()
		self._dlgdirectory.hide()
		if response == gtk.RESPONSE_OK:
			value = self._dlgdirectory.get_filename()
			self._on_value_changed(c, iter, value)
		return
	
	def _on_combo_set(self, c, iter):
		if not self._dlgcombo:
			self._dlgcombo = ComboDialog()
		self._dlgcombo.set_preset(c.name)
		self._dlgcombo.set_selection(c.value)
		response = self._dlgcombo.run()
		self._dlgcombo.hide()
		if response == gtk.RESPONSE_OK:
			value = self._dlgcombo.get_selection()
			self._on_value_changed(c, iter, value)
		return
		
	def _on_row_activated(self, treeview, path, column):
		iter = self._model.get_iter(path)
		name = self._model.get_value(iter, 0)
		c = self._setting[name]
		if not c.readonly:
			value = None
			if c.name in engine_map.keys() + ['main.download', 
				'display.embedded', 'display.roller', 'display.gosd']:
				self._on_bool_set(c, iter)
			elif c.name in ['display.embedded.foreground', 'display.embedded.background',
				'display.roller.foreground', 'display.roller.background']:
				self._on_color_set(c, iter)
			elif c.name in ['display.embedded.font', 'display.roller.font']:
				self._on_font_set(c, iter)
			elif c.name == 'main.directory':
				self._on_directory_set(c, iter)
			elif c.name == 'main.file_pattern':
				self._on_combo_set(c, iter)
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
	
	def set(self, name, value, watch = True):
		config = self._setting[name]
		iter = self._model.get_iter_first()
		while iter != None:
			if name == self._model.get_value(iter, 0):
				break
			iter = self._model.iter_next(iter)
		self._on_value_changed(config, iter, value, watch)
		return
		
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
