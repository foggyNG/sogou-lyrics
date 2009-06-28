import os, gobject, gtk, gtk.glade, gtk.gdk, gconf

gconf_keys = {
'display' : '/apps/rhythmbox/plugins/SogouLyrics/display',
'download' : '/apps/rhythmbox/plugins/SogouLyrics/download',
'halign' : '/apps/rhythmbox/plugins/SogouLyrics/halign',
'vpos' : '/apps/rhythmbox/plugins/SogouLyrics/vpos',
'fgcolor' : '/apps/rhythmbox/plugins/SogouLyrics/fgcolor',
'animation' : '/apps/rhythmbox/plugins/SogouLyrics/animation',
'folder' : '/apps/rhythmbox/plugins/SogouLyrics/folder',
'engine' : '/apps/rhythmbox/plugins/SogouLyrics/engine'
}
engines = ['Sogou', 'ttPlayer']

class Preference (object):
	def __init__(self, glade_file):
		print 'enter'
		# get main dialog frome glade file
		self.gconf = gconf.client_get_default()
		self.gladexml = gtk.glade.XML(glade_file)
		self.dialog = self.gladexml.get_widget('preference')
		self.dialog.connect('response', self.dialog_response)
		# get widgets from glade file
		self.widgets = {}
		for key in ['display','download','halign','vpos','fgcolor','animation','folder','Sogou','ttPlayer']:
			self.widgets[key] = self.gladexml.get_widget(key)
		filter = gtk.FileFilter()
		filter.add_mime_type('inode/directory')
		self.widgets['folder'].set_filter(filter)
		# load settings
		self.settings = {}
		self.load_prefs()
		print 'leave'
		return
		
	def dialog_response(self, dialog, response):
		dialog.hide()
	
	def set_display(self, widget):
		key = 'display'
		value = widget.get_active()
		self.settings[key] = value
		self.gconf.set_bool(gconf_keys[key], value)
		print '%s : %d' % (key, value)
		return
	
	def set_download(self, widget):
		key = 'download'
		value = widget.get_active()
		self.settings[key] = value
		self.gconf.set_bool(gconf_keys[key], value)
		print '%s : %d' % (key, value)
		return
		
	def set_halign(self, widget):
		key = 'halign'
		value = widget.get_active_text()
		self.settings[key] = value
		self.gconf.set_string(gconf_keys[key], value)
		print '%s : %s' % (key, value)
		return
		
	def set_vpos(self, widget):
		key = 'vpos'
		value = widget.get_active_text()
		self.settings[key] = value
		self.gconf.set_string(gconf_keys[key], value)
		print '%s : %s' % (key, value)
		return
		
	def set_fgcolor(self, widget):
		key = 'fgcolor'
		value = widget.get_color().to_string()
		self.settings[key] = value
		self.gconf.set_string(gconf_keys[key], value)
		print '%s : %s' % (key, value)
		return
		
	def set_animation(self, widget):
		key = 'animation'
		value = widget.get_active_text()
		self.settings[key] = value
		self.gconf.set_string(gconf_keys[key], value)
		print '%s : %s' % (key, value)
		return
		
	def set_folder(self, widget):
		key = 'folder'
		value = widget.get_filename()
		self.settings[key] = value
		self.gconf.set_string(gconf_keys[key], value)
		print '%s : %s' % (key, value)
		return

	def set_engine(self, widget):
		key = 'engine'
		widget_key = widget.get_name()
		value = self.settings[key]
		if widget.get_active() and not widget_key in value:
			value.append(widget_key)
		elif not widget.get_active() and widget_key in value:
			value.remove(widget_key)
		self.settings[key] = value
		self.gconf.set_list(gconf_keys[key], gconf.VALUE_STRING, value)
		print '%s : %s' % (key, value)
		return
		
	def get_dialog (self):
		return self.dialog
	
	def get_pref(self, key):
		return self.settings[key]
		
	def load_prefs (self):
		self.settings['engine'] = ['Sogou']
		print 'enter'
		# display
		key = 'display'
		value = None
		widget = self.widgets[key]
		try:
			value = self.gconf.get_bool(gconf_keys[key])
		except:
			value = True
		self.settings[key] = value
		print '%s : %d' % (key, value)
		widget.set_active(value)
		widget.connect('toggled', self.set_display)
		# download
		key = 'download'
		value = None
		widget = self.widgets[key]
		try:
			value = self.gconf.get_bool(gconf_keys[key])
		except:
			value = True
		self.settings[key] = value
		print '%s : %d' % (key, value)
		widget.set_active(value)
		widget.connect('toggled', self.set_download)
		# halign
		key = 'halign'
		value = None
		widget = self.widgets[key]
		model = widget.get_model()
		index = 0
		try:
			value = self.gconf.get_string(gconf_keys[key])
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
		self.settings[key] = value
		print '%s : %s' % (key, value)
		widget.set_active(index)
		widget.connect('changed', self.set_halign)
		# vpos
		key = 'vpos'
		value = None
		widget = self.widgets[key]
		model = widget.get_model()
		index = 0
		try:
			value = self.gconf.get_string(gconf_keys[key])
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
		self.settings[key] = value
		print '%s : %s' % (key, value)
		widget.set_active(index)
		widget.connect('changed', self.set_vpos)
		# fgcolor
		key = 'fgcolor'
		value = None
		widget = self.widgets[key]
		try:
			value = self.gconf.get_string(gconf_keys[key])
			gtk.gdk.color_parse(value)
		except:
			value = '#FFFF00'
		self.settings[key] = value
		print '%s : %s' % (key, value)
		widget.set_color(gtk.gdk.color_parse(value))
		widget.connect('color-set', self.set_fgcolor)
		# animation
		key = 'animation'
		value = None
		widget = self.widgets[key]
		model = widget.get_model()
		index = 0
		try:
			value = self.gconf.get_string(gconf_keys[key])
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
		self.settings[key] = value
		print '%s : %s' % (key, value)
		widget.set_active(index)
		widget.connect('changed', self.set_animation)
		# folder
		key = 'folder'
		value = None
		widget = self.widgets[key]
		try:
			value = self.gconf.get_string(gconf_keys[key])
			if not value:
				value = os.path.expanduser('~/.lyrics')
		except:
			value = os.path.expanduser('~/.lyrics')
		self.settings[key] = value
		print '%s : %s' % (key, value)
		widget.set_filename(value)
		widget.connect('file-set', self.set_folder)
		# pygtk bug
		widget.connect('selection-changed', self.set_folder)
		# engine
		key = 'engine'
		value = None
		try:
			value = self.gconf.get_list(self.gconf_keys['engine'], gconf.VALUE_STRING)
			if value is None:
				value = engines
		except:
			value = engines
		self.settings[key] = value
		print '%s : %s' % (key, value)
		for engine in engines:
			self.widgets[engine].set_active(engine in value)
			self.widgets[engine].connect('toggled', self.set_engine)
		print 'leave'
		return
