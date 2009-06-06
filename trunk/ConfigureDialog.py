import gobject, gtk, gtk.glade
import gconf
from os import system, path

class ConfigureDialog (object):
	def __init__(self, glade_file, gconf_keys):
		self.gconf = gconf.client_get_default()
		self.gconf_keys = gconf_keys
		
		self.gladexml = gtk.glade.XML(glade_file)
		self.dialog = self.gladexml.get_widget("preferences_dialog")
		self.toggle_hide = self.gladexml.get_widget("hide")
		self.toggle_offline = self.gladexml.get_widget("offline")
		self.dialog.connect("response", self.dialog_response)
		# set fields from gconf
		settings = self.get_prefs()
		self.toggle_hide.set_active(settings['hide'])
		self.toggle_offline.set_active(settings['offline'])


	def dialog_response(self, dialog, response):
		if response == gtk.RESPONSE_OK:
			self.set_values()
			self.dialog.hide()
		elif response == gtk.RESPONSE_CANCEL or response == gtk.RESPONSE_DELETE_EVENT:
			self.dialog.hide()
		else:
			print "unexpected response type"

	def set_values(self):
		self.gconf.set_bool(self.gconf_keys['hide'], self.toggle_hide.get_active())
		self.gconf.set_bool(self.gconf_keys['offline'], self.toggle_offline.get_active())

	def get_dialog (self):
		return self.dialog
	
	def get_prefs (self):
		hide = gconf.client_get_default().get_bool(self.gconf_keys['hide'])
		offline = gconf.client_get_default().get_bool(self.gconf_keys['offline'])
		return {'hide':hide, 'offline':offline}
