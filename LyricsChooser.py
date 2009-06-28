import os, gobject, gtk, gtk.glade, gtk.gdk, gconf

class LyricsChooser:
	def __init__(self, glade_file):
		print 'enter'
		# get main dialog frome glade file
		self.gconf = gconf.client_get_default()
		self.gladexml = gtk.glade.XML(glade_file)
		self.window = self.gladexml.get_widget('lyrics-chooser')
		# get widgets from glade file
		self.widgets = {}
		for key in ['chooser', 'preview', 'ok', 'close']:
			self.widgets[key] = self.gladexml.get_widget(key)
		self.widgets['ok'].connect('clicked', self.response, gtk.RESPONSE_OK)
		self.widgets['close'].connect('clicked', self.response, gtk.RESPONSE_CLOSE)
		print 'leave'
		return
		
	def response(self, widget, response):
		if response == gtk.RESPONSE_OK:
			print 'choosed'
		self.window.hide()
		return
	
	def set_candidates(self, candidates):
		
		return
	
	def get_window (self):
		return self.window
