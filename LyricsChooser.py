#!/usr/bin/env python
#-*- coding: UTF-8 -*-

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

import gobject, gtk, gettext
from gtk.glade import XML

from utils import log
_ = gettext.gettext

class LyricsChooser:
	def __init__(self, glade_file, callback):
		log.debug('enter')
		gladexml = XML(glade_file)
		self.__window = gladexml.get_widget('lyrics-chooser')
		self.__callback = callback
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
		log.debug('leave')
		return
		
	def __selection_changed(self, widget):
		log.debug('enter')
		selected = widget.get_selected()
		if selected[1]:
			index = selected[0].get_value(selected[1], 0)
			log.debug('select [index = %d]' % index)
			self.__viewer.get_buffer().set_text(self.__candidate[index][1].get_raw())
		else:
			self.__viewer.get_buffer().set_text('')
		log.debug('leave')
		return
		
	def __response(self, widget, response):
		log.debug('enter')
		lyrics = None
		if response == gtk.RESPONSE_OK:
			selected = self.__chooser.get_selection().get_selected()
			index = selected[0].get_value(selected[1], 0)
			lyrics = self.__candidate[index][1]
		self.__window.hide()
		self.__callback(self.__songinfo, lyrics)
		log.debug('leave')
		return
	
	def set_instance(self, songinfo, candidate):
		log.debug('enter')
		self.__songinfo = songinfo
		self.__token.clear()
		self.__candidate = candidate
		count = 0
		for c in self.__candidate:
			self.__token.append([count, '%s - %s' % (c[1].get('ar'), c[1].get('ti'))])
			count = count + 1
		self.__chooser.get_selection().select_iter(self.__token.get_iter_first())
		log.debug('leave')
		return
		
	def show(self):
		log.debug('enter')
		self.__window.set_title('%s - %s' % (self.__songinfo.get('ar'), self.__songinfo.get('ti')))
		self.__window.show_all()
		log.debug('enter')
		return
