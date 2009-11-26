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

log = logging.getLogger('RBLyrics')

## Lyrics chooser dialog.
class LyricsChooser:
	
	## The constructor.
	#  @param callback Response callback.
	def __init__(self, callback):
		log.debug('enter')
		self._dialog = gtk.Dialog(flags = gtk.DIALOG_NO_SEPARATOR, buttons = (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		self._dialog.set_default_size(640, 480)
		self._callback = callback
		self._lyrics = None
		self._song = None
		#
		self._model = gtk.ListStore(int, str, str, int)
		treeview = gtk.TreeView(self._model)
		treeview.append_column(gtk.TreeViewColumn('', gtk.CellRendererText(), text = 0))
		treeview.append_column(gtk.TreeViewColumn(_('Artist'), gtk.CellRendererText(), text = 1))
		treeview.append_column(gtk.TreeViewColumn(_('Title'), gtk.CellRendererText(), text = 2))
		self._selection = treeview.get_selection()
		self._selection.connect('changed', self._selection_changed)
		self._viewer = gtk.TextView()
		self._viewer.set_editable(False)
		self._viewer.set_cursor_visible(False)
		#
		panel = gtk.HPaned()
		scroll = gtk.ScrolledWindow()
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll.add_with_viewport(treeview)
		panel.pack1(scroll, False, False)
		scroll = gtk.ScrolledWindow()
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll.add_with_viewport(self._viewer)
		panel.pack2(scroll, False, False)
		panel.set_position(180)
		self._dialog.get_content_area().add(panel)
		self._dialog.get_content_area().show_all()
		#
		self._dialog.connect('delete-event', self._on_delete_event)
		self._dialog.connect('response', self._on_response)
		log.debug('leave')
		return
	
	## Selection changed handler.
	def _selection_changed(self, widget):
		log.debug('enter')
		selected = widget.get_selected()
		if selected[1]:
			index = selected[0].get_value(selected[1], 3)
			log.debug('select [index = %d]' % index)
			self._viewer.get_buffer().set_text(self._candidate[index][1].get_raw())
		else:
			self._viewer.get_buffer().set_text('')
		log.debug('leave')
		return
	
	## Dialog response handler.
	def _on_response(self, dialog, response_id):
		log.debug('enter <%d>' % response_id)
		if response_id == gtk.RESPONSE_OK:
			selected = self._selection.get_selected()
			index = selected[0].get_value(selected[1], 3)
			lyrics = self._candidate[index][1]
			dialog.hide()
			self._callback(self._songinfo, lyrics)
		else:
			dialog.hide()
			self._callback(self._songinfo, None)
		log.debug('leave')
		return
	
	def _on_delete_event(self, widget, event):
		widget.hide()
		self._callback(self._songinfo, None)
		return True
	
	## Set choosing instance.
	#  @param songinfo Song information to be chosen.
	#  @param candidate Lyrics candidates to be chosen.
	def set_instance(self, songinfo, candidate):
		log.debug('enter')
		self._songinfo = songinfo
		self._dialog.set_title('%s - %s' % (self._songinfo.get('ar'), self._songinfo.get('ti')))
		self._model.clear()
		self._candidate = candidate
		count = 0
		for c in self._candidate:
			self._model.append([c[0], c[1].get('ar'), c[1].get('ti'), count])
			count = count + 1
		self._selection.select_iter(self._model.get_iter_first())
		self._dialog.show()
		log.debug('leave')
		return

