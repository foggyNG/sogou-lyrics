#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, gobject, gtk, gtk.glade, gtk.gdk, gconf, logging, gettext
_ = gettext.gettext
class LyricsChooser:
	def __init__(self, glade_file):
		logging.debug('enter')
		# get main dialog frome glade file
		#gconf = gconf.client_get_default()
		gladexml = gtk.glade.XML(glade_file)
		self.__window = gladexml.get_widget('lyrics-chooser')
		# get widgets from glade file
		widgets = {}
		for key in ['chooser', 'preview', 'ok', 'close']:
			widgets[key] = gladexml.get_widget(key)
		widgets['ok'].connect('clicked', self.__response, gtk.RESPONSE_OK)
		widgets['close'].connect('clicked', self.__response, gtk.RESPONSE_CLOSE)
		#
		self.__token = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
		self.__lyrics = None
		self.__song = None
		self.__chooser = widgets['chooser']
		self.__chooser.append_column(gtk.TreeViewColumn(_('Artist - Title'), gtk.CellRendererText(), text=1))
		self.__chooser.set_model(self.__token)
		selection = self.__chooser.get_selection()
		selection.connect('changed', self.__selection_changed)
		self.__viewer = widgets['preview']
		del selection, widgets, gladexml
		logging.debug('leave')
		return
		
	def __selection_changed(self, widget):
		selected = widget.get_selected()
		if selected[1]:
			index = selected[0].get_value(selected[1], 0)
			logging.debug('select [index = %d]' % index)
			self.__viewer.get_buffer().set_text(self.__lyrics[index].raw_)
		else:
			self.__viewer.get_buffer().set_text('')
		return
		
	def __response(self, widget, response):
		if response == gtk.RESPONSE_OK:
			selected = self.__chooser.get_selection().get_selected()
			index = selected[0].get_value(selected[1], 0)
			self.__lyrics[index].save_lyrics()
		self.__window.hide()
		return
	
	def set_instance(self, lyrics, song):
		logging.debug('enter')
		self.__song = song
		self.__token.clear()
		self.__lyrics = lyrics
		count = 0
		for c in lyrics:
			ar = ''
			if c.lrcinfo_.has_key('ar'):
				ar = c.lrcinfo_['ar']
			ti = ''
			if c.lrcinfo_.has_key('ti'):
				ti = c.lrcinfo_['ti']
			self.__token.append([count, '%s - %s' % (ar, ti)])
			count = count + 1
		self.__chooser.get_selection().select_iter(self.__token.get_iter_first())
		logging.debug('leave')
		return
		
	def show(self):
		self.__window.set_title('%s - %s' % (self.__song.songinfo_['ar'], self.__song.songinfo_['ti']))
		self.__window.show_all()
		return
