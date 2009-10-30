#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, gobject, gtk, gtk.glade, gtk.gdk, gconf, logging
from Engine import engine_map
gconf_keys = {
'display' : '/apps/rhythmbox/plugins/RBLyrics/display',
'download' : '/apps/rhythmbox/plugins/RBLyrics/download',
'halign' : '/apps/rhythmbox/plugins/RBLyrics/halign',
'vpos' : '/apps/rhythmbox/plugins/RBLyrics/vpos',
'fgcolor' : '/apps/rhythmbox/plugins/RBLyrics/fgcolor',
'animation' : '/apps/rhythmbox/plugins/RBLyrics/animation',
'folder' : '/apps/rhythmbox/plugins/RBLyrics/folder',
'engine' : '/apps/rhythmbox/plugins/RBLyrics/engine'
}

class Preference:
	def __init__(self, glade_file):
		logging.debug('enter')
		# get main dialog frome glade file
		self.__gconf = gconf.client_get_default()
		gladexml = gtk.glade.XML(glade_file)
		self.__dialog = gladexml.get_widget('preference')
		self.__dialog.connect('response', self.__dialog_response)
		# get widgets from glade file
		self.__widget = {}
		for key in ['display','download','halign','vpos','fgcolor','animation','folder'] + engine_map.keys():
			self.__widget[key] = gladexml.get_widget(key)
		filter = gtk.FileFilter()
		filter.add_mime_type('inode/directory')
		self.__widget['folder'].set_filter(filter)
		# load settings
		self.__setting = {}
		self.__load_prefs()
		logging.debug('leave')
		return
		
	def __dialog_response(self, dialog, response):
		dialog.hide()
		return
	
	def set_display(self, widget):
		key = 'display'
		value = widget.get_active()
		self.__setting[key] = value
		self.__gconf.set_bool(gconf_keys[key], value)
		logging.info('%s : %s' % (key, value))
		return
	
	def set_download(self, widget):
		key = 'download'
		value = widget.get_active()
		self.__setting[key] = value
		self.__gconf.set_bool(gconf_keys[key], value)
		logging.info('%s : %s' % (key, value))
		return
		
	def set_halign(self, widget):
		key = 'halign'
		value = widget.get_active_text()
		self.__setting[key] = value
		self.__gconf.set_string(gconf_keys[key], value)
		logging.info('%s : %s' % (key, value))
		return
		
	def set_vpos(self, widget):
		key = 'vpos'
		value = widget.get_active_text()
		self.__setting[key] = value
		self.__gconf.set_string(gconf_keys[key], value)
		logging.info('%s : %s' % (key, value))
		return
		
	def set_fgcolor(self, widget):
		key = 'fgcolor'
		value = widget.get_color().to_string()
		self.__setting[key] = value
		self.__gconf.set_string(gconf_keys[key], value)
		logging.info('%s : %s' % (key, value))
		return
		
	def set_animation(self, widget):
		key = 'animation'
		value = widget.get_active_text()
		self.__setting[key] = value
		self.__gconf.set_string(gconf_keys[key], value)
		logging.info('%s : %s' % (key, value))
		return
		
	def set_folder(self, widget):
		key = 'folder'
		value = widget.get_filename()
		self.__setting[key] = value
		self.__gconf.set_string(gconf_keys[key], value)
		logging.info('%s : %s' % (key, value))
		return

	def set_engine(self, widget):
		key = 'engine'
		widget_key = widget.get_name()
		value = self.__setting[key]
		if widget.get_active() and not widget_key in value:
			value.append(widget_key)
		elif not widget.get_active() and widget_key in value:
			value.remove(widget_key)
		self.__setting[key] = value
		self.__gconf.set_list(gconf_keys[key], gconf.VALUE_STRING, value)
		logging.info('%s : %s' % (key, value))
		return
		
	def get_dialog (self):
		return self.__dialog
	
	def get(self, key):
		return self.__setting[key]
		
	def __load_prefs (self):
		logging.debug('enter')
		# display
		key = 'display'
		value = None
		widget = self.__widget[key]
		try:
			value = self.__gconf.get_bool(gconf_keys[key])
		except:
			value = True
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		widget.set_active(value)
		widget.connect('toggled', self.set_display)
		# download
		key = 'download'
		value = None
		widget = self.__widget[key]
		try:
			value = self.__gconf.get_bool(gconf_keys[key])
		except:
			value = True
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		widget.set_active(value)
		widget.connect('toggled', self.set_download)
		# halign
		key = 'halign'
		value = None
		widget = self.__widget[key]
		model = widget.get_model()
		index = 0
		try:
			value = self.__gconf.get_string(gconf_keys[key])
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
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		widget.set_active(index)
		widget.connect('changed', self.set_halign)
		# vpos
		key = 'vpos'
		value = None
		widget = self.__widget[key]
		model = widget.get_model()
		index = 0
		try:
			value = self.__gconf.get_string(gconf_keys[key])
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
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		widget.set_active(index)
		widget.connect('changed', self.set_vpos)
		# fgcolor
		key = 'fgcolor'
		value = None
		widget = self.__widget[key]
		try:
			value = self.__gconf.get_string(gconf_keys[key])
			gtk.gdk.color_parse(value)
		except:
			value = '#FFFF00'
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		widget.set_color(gtk.gdk.color_parse(value))
		widget.connect('color-set', self.set_fgcolor)
		# animation
		key = 'animation'
		value = None
		widget = self.__widget[key]
		model = widget.get_model()
		index = 0
		try:
			value = self.__gconf.get_string(gconf_keys[key])
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
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		widget.set_active(index)
		widget.connect('changed', self.set_animation)
		# folder
		key = 'folder'
		value = None
		widget = self.__widget[key]
		try:
			value = self.__gconf.get_string(gconf_keys[key])
			if not value:
				value = os.path.expanduser('~/.lyrics')
		except:
			value = os.path.expanduser('~/.lyrics')
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		widget.set_filename(value)
		widget.connect('file-set', self.set_folder)
		# pygtk bug
		# widget.connect('selection-changed', self.set_folder)
		# engine
		key = 'engine'
		value = None
		try:
			value = self.__gconf.get_list(gconf_keys[key], gconf.VALUE_STRING)
			if value is None:
				value = engine_map.keys()
		except:
			value = engine_map.keys()
		self.__setting[key] = value
		logging.info('%s : %s' % (key, value))
		for engine in engine_map.keys():
			self.__widget[engine].set_active(engine in value)
			self.__widget[engine].connect('toggled', self.set_engine)
		logging.debug('leave')
		return
