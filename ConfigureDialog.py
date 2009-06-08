import gobject, gtk, gtk.glade
import gconf
from os import system, path

gconf_keys = {
'hide' : '/apps/rhythmbox/plugins/SogouLyrics/hide',
'offline' : '/apps/rhythmbox/plugins/SogouLyrics/offline',
'halign' : '/apps/rhythmbox/plugins/SogouLyrics/halign',
'vpos' : '/apps/rhythmbox/plugins/SogouLyrics/vpos',
'fgcolor' : '/apps/rhythmbox/plugins/SogouLyrics/fgcolor',
'animation' : '/apps/rhythmbox/plugins/SogouLyrics/animation'
}
PRESET = {
'halign' : ['center', 'left', 'right'],
'vpos' : ['top', 'center', 'bottom'],
'fgcolor' : ['yellow', 'red', 'green', 'blue'],
'animation' : ['off', 'on']
}
class ConfigureDialog (object):
	def __init__(self, glade_file):
		self.gconf = gconf.client_get_default()
		self.gladexml = gtk.glade.XML(glade_file)
		#
		self.dialog = self.gladexml.get_widget('preferences_dialog')
		self.dialog.connect('response', self.dialog_response)
		#
		self.widgets = {}
		for key in gconf_keys.keys():
			self.widgets[key] = self.gladexml.get_widget(key)
		for key in ['halign', 'vpos', 'fgcolor', 'animation']:
			liststore = gtk.ListStore(gobject.TYPE_STRING)
			for value in PRESET[key]:
				liststore.append([value])
			self.widgets[key].set_model(liststore)
		# load settings
		self.settings = {}
		self.get_prefs()
		for key in ['hide', 'offline']:
			self.widgets[key].set_active(self.settings[key])
			self.widgets[key].connect('toggled', self.set_prefs)
		for key in ['halign', 'vpos', 'fgcolor', 'animation']:
			self.widgets[key].set_active(PRESET[key].index(self.settings[key]))
			self.widgets[key].connect('changed', self.set_prefs)

	def dialog_response(self, dialog, response):
		dialog.hide()

	def set_prefs(self, widget):
		for key in ['hide', 'offline']:
			value = self.widgets[key].get_active()
			self.settings[key] = value
			self.gconf.set_bool(gconf_keys[key], value)
		for key in ['halign', 'vpos', 'fgcolor', 'animation']:
			value = PRESET[key][self.widgets[key].get_active()]
			self.settings[key] = value
			self.gconf.set_string(gconf_keys[key], value)

	def get_dialog (self):
		return self.dialog
	
	def get_config(self, key):
		return self.settings[key]
		
	def get_prefs (self):
		for prop in ['hide', 'offline']:
			self.settings[prop] = self.gconf.get_bool(gconf_keys[prop])
		for prop in ['halign', 'vpos', 'fgcolor', 'animation']:
			value = self.gconf.get_string(gconf_keys[prop])
			if not value:
				value = PRESET[prop][0]
			try:
				index = PRESET[prop].index(value)
			except ValueError:
				value = PRESET[prop][0]
			self.settings[prop] = value
		return
