import gobject, gtk, gtk.glade, gtk.gdk, gconf

gconf_keys = {
'display' : '/apps/rhythmbox/plugins/SogouLyrics/display',
'download' : '/apps/rhythmbox/plugins/SogouLyrics/download',
'halign' : '/apps/rhythmbox/plugins/SogouLyrics/halign',
'vpos' : '/apps/rhythmbox/plugins/SogouLyrics/vpos',
'fgcolor' : '/apps/rhythmbox/plugins/SogouLyrics/fgcolor',
'animation' : '/apps/rhythmbox/plugins/SogouLyrics/animation'
}
class Preference (object):
	def __init__(self, glade_file):
		self.gconf = gconf.client_get_default()
		self.gladexml = gtk.glade.XML(glade_file)
		#
		self.dialog = self.gladexml.get_widget('preference')
		self.dialog.connect('response', self.dialog_response)
		#
		self.widgets = {}
		for key in gconf_keys.keys():
			self.widgets[key] = self.gladexml.get_widget(key)
		# load settings
		self.settings = {}
		self.load_prefs()
		for key in gconf_keys.keys():
			widget = self.widgets[key];
			widget_type = widget.__class__.__name__
			value = self.settings[key]
			if widget_type in ['ComboBox']:
				model = widget.get_model()
				iter = model.get_iter_first()
				index = 0
				while iter:
					if model.get_value(iter,0) == value:
						widget.set_active(index)
						break
					else:
						index += 1
						iter = model.iter_next(iter)
				widget.connect('changed', self.set_pref)
			elif widget_type in ['ColorButton']:
				widget.set_color(gtk.gdk.Color(value))
				widget.connect('color-set', self.set_pref)
			elif widget_type in ['CheckButton']:
				widget.set_active(value)
				widget.connect('toggled', self.set_pref)
			else:
				print 'unknown widget type : %s' % widget_type
		return
		
		
		
	def dialog_response(self, dialog, response):
		dialog.hide()

	def set_pref(self, widget):
		print 'enter'
		key = widget.get_name()
		widget_type = widget.__class__.__name__
		if widget_type in ['ComboBox']:
			value = widget.get_active_text()
			self.settings[key] = value
			self.gconf.set_string(gconf_keys[key], value)
			print '%s : %s' % (key, value)
		elif widget_type in ['ColorButton']:
			value = widget.get_color().to_string()
			self.settings[key] = value
			self.gconf.set_string(gconf_keys[key], value)
			print '%s : %s' % (key, value)
		elif widget_type in ['CheckButton']:
			value = widget.get_active()
			self.settings[key] = value
			self.gconf.set_bool(gconf_keys[key], value)
			print '%s : %d' % (key, value)
		else:
			print 'unknown widget type : %s' % widget_type
		print 'leave'
		return

	def get_dialog (self):
		return self.dialog
	
	def get_pref(self, key):
		return self.settings[key]
		
	def load_prefs (self):
		print 'enter'
		for key in gconf_keys.keys():
			widget = self.widgets[key]
			widget_type = widget.__class__.__name__
			if widget_type in ['ComboBox']:
				model = widget.get_model()
				try:
					value = self.gconf.get_string(gconf_keys[key])
					iter = model.get_iter_first()
					found = False
					while iter:
						if model.get_value(iter,0) == value:
							found = True
							break
						else:
							iter = model.iter_next(iter)
					if not found :
						value = model.get_value(model.get_iter_first(), 0)
				except:
					value = model.get_value(model.get_iter_first(), 0)
				self.settings[key] = value
				print '%s : %s' % (key, value)
			elif widget_type in ['ColorButton']:
				try:
					value = self.gconf.get_string(gconf_keys[key])
					gtk.gdk.color_parse(value)
				except:
					value = 'yellow'
				self.settings[key] = value
				print '%s : %s' % (key, value)
			elif widget_type in ['CheckButton']:
				try:
					value = self.gconf.get_bool(gconf_keys[key])
				except:
					value = True
				self.settings[key] = value
				print '%s : %d' % (key, value)
			else:
				print 'unknown widget type : %s' % widget_type
		print 'leave'
		return
