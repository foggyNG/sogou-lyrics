#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#
#       
#       Copyright 2009 wonder <gogo.wonder@gmail.com>
#       
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

## @package RBLyrics.chooser
#  Lyrics chooser.

import gobject, gtk, gettext, logging
_ = gettext.gettext
from gtk.glade import XML

log = logging.getLogger('RBLyrics')

## Lyrics chooser dialog.
class LyricsChooser:
	
	## The constructor.
	#  @param glade_file UI glade file.
	#  @param callback Response callback.
	def __init__(self, glade_file, callback):
		log.debug('enter')
		gladexml = XML(glade_file)
		self._window = gladexml.get_widget('lyrics-chooser')
		self._callback = callback
		widgets = {}
		for key in ['chooser', 'preview', 'ok', 'close']:
			widgets[key] = gladexml.get_widget(key)
		widgets['ok'].connect('clicked', self._response, gtk.RESPONSE_OK)
		widgets['close'].connect('clicked', self._response, gtk.RESPONSE_CLOSE)
		#
		self._token = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
		self._lyrics = None
		self._song = None
		self._chooser = widgets['chooser']
		self._chooser.append_column(gtk.TreeViewColumn(_('Artist - Title'), gtk.CellRendererText(), text=1))
		self._chooser.set_model(self._token)
		selection = self._chooser.get_selection()
		selection.connect('changed', self._selection_changed)
		self._viewer = widgets['preview']
		del selection, widgets, gladexml
		log.debug('leave')
		return
	
	## Selection changed handler.
	def _selection_changed(self, widget):
		log.debug('enter')
		selected = widget.get_selected()
		if selected[1]:
			index = selected[0].get_value(selected[1], 0)
			log.debug('select [index = %d]' % index)
			self._viewer.get_buffer().set_text(self._candidate[index][1].get_raw())
		else:
			self._viewer.get_buffer().set_text('')
		log.debug('leave')
		return
	
	## Dialog response handler.
	def _response(self, widget, response):
		log.debug('enter')
		lyrics = None
		if response == gtk.RESPONSE_OK:
			selected = self._chooser.get_selection().get_selected()
			index = selected[0].get_value(selected[1], 0)
			lyrics = self._candidate[index][1]
		self._window.hide()
		self._callback(self._songinfo, lyrics)
		log.debug('leave')
		return
	
	## Set choosing instance.
	#  @param songinfo Song information to be chosen.
	#  @param candidate Lyrics candidates to be chosen.
	def set_instance(self, songinfo, candidate):
		log.debug('enter')
		self._songinfo = songinfo
		self._token.clear()
		self._candidate = candidate
		count = 0
		for c in self._candidate:
			self._token.append([count, '%s - %s' % (c[1].get('ar'), c[1].get('ti'))])
			count = count + 1
		self._chooser.get_selection().select_iter(self._token.get_iter_first())
		log.debug('leave')
		return
	
	## Show dialog.
	def show(self):
		log.debug('enter')
		self._window.set_title('%s - %s' % (self._songinfo.get('ar'), self._songinfo.get('ti')))
		self._window.show_all()
		log.debug('enter')
		return
