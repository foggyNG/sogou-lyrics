#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, gobject, gtk, gtk.glade, gtk.gdk, gconf, logging, string

class LyricsChooser:
	def __init__(self, glade_file):
		logging.debug('enter')
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
		#
		self.lrc_path = None
		self.token = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
		self.lyrics = []
		self.chooser = self.widgets['chooser']
		self.chooser.append_column(gtk.TreeViewColumn('Artist - Title', gtk.CellRendererText(), text=1))
		self.chooser.set_model(self.token)
		selection = self.chooser.get_selection()
		selection.connect('changed', self.selection_changed)
		self.viewer = self.widgets['preview']
		logging.debug('leave')
		return
		
	def selection_changed(self, widget):
		logging.debug('enter')
		selected = widget.get_selected()
		if selected[1]:
			index = selected[0].get_value(selected[1], 0)
			logging.info('select <index=%d>' % index)
			self.viewer.get_buffer().set_text(self.lyrics[index])
		else:
			self.viewer.get_buffer().set_text('')
		logging.debug('leave')
		return
		
	def response(self, widget, response):
		if response == gtk.RESPONSE_OK:
			dir = os.path.dirname(self.lrc_path)
			if not os.path.exists(dir):
				os.makedirs(dir)
			buffer = self.viewer.get_buffer()
			open(self.lrc_path, 'w').write(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter()))
		self.window.hide()
		return
	
	def set_instance(self, candidates, lrc_path):
		logging.debug('enter')
		self.lrc_path = lrc_path
		self.token.clear()
		self.lyrics = []
		count = 0
		for c in candidates:
			self.token.append([count, '%s - %s' % (c[0], c[1])])
			count = count + 1
			self.lyrics.append(string.join(c[2], ''))
		#
		self.chooser.get_selection().select_iter(self.token.get_iter_first())
		logging.debug('leave')
		return
		
	def show(self, artist, title):
		self.window.set_title('%s - %s' % (artist, title))
		self.window.show_all()
		return
