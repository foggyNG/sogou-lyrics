#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, gobject, gtk, gtk.glade, gtk.gdk, gconf, logging
from utils import _
class LyricsChooser:
	def __init__(self, glade_file):
		logging.debug('enter')
		# get main dialog frome glade file
		#gconf = gconf.client_get_default()
		gladexml = gtk.glade.XML(glade_file)
		self.window_ = gladexml.get_widget('lyrics-chooser')
		# get widgets from glade file
		widgets = {}
		for key in ['chooser', 'preview', 'ok', 'close']:
			widgets[key] = gladexml.get_widget(key)
		widgets['ok'].connect('clicked', self.response, gtk.RESPONSE_OK)
		widgets['close'].connect('clicked', self.response, gtk.RESPONSE_CLOSE)
		#
		self.token_ = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
		self.lyrics_ = None
		self.song_ = None
		self.chooser_ = widgets['chooser']
		self.chooser_.append_column(gtk.TreeViewColumn(_('Artist - Title'), gtk.CellRendererText(), text=1))
		self.chooser_.set_model(self.token_)
		selection = self.chooser_.get_selection()
		selection.connect('changed', self.selection_changed)
		self.viewer_ = widgets['preview']
		del selection, widgets, gladexml
		logging.debug('leave')
		return
		
	def selection_changed(self, widget):
		logging.debug('enter')
		selected = widget.get_selected()
		if selected[1]:
			index = selected[0].get_value(selected[1], 0)
			logging.debug('select <index=%d>' % index)
			self.viewer_.get_buffer().set_text(self.lyrics_[index].raw_)
		else:
			self.viewer_.get_buffer().set_text('')
		logging.debug('leave')
		return
		
	def response(self, widget, response):
		if response == gtk.RESPONSE_OK:
			selected = self.chooser_.get_selection().get_selected()
			index = selected[0].get_value(selected[1], 0)
			self.lyrics_[index].save()
		self.window_.hide()
		return
	
	def set_instance(self, lyrics, song):
		logging.debug('enter')
		self.song_ = song
		self.token_.clear()
		self.lyrics_ = lyrics
		count = 0
		for c in lyrics:
			ar = ''
			if c.lrcinfo_.has_key('ar'):
				ar = c.lrcinfo_['ar']
			ti = ''
			if c.lrcinfo_.has_key('ti'):
				ti = c.lrcinfo_['ti']
			self.token_.append([count, '%s - %s' % (ar, ti)])
			count = count + 1
		#
		self.chooser_.get_selection().select_iter(self.token_.get_iter_first())
		logging.debug('leave')
		return
		
	def show(self):
		self.window_.set_title('%s - %s' % (self.song_.songinfo_['ar'], self.song_.songinfo_['ti']))
		self.window_.show_all()
		return
