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
#  歌词选择对话框。

import gtk, gettext, logging
_ = gettext.gettext
log = logging.getLogger('RBLyrics')

## 歌词选择对话框。
class LyricsChooser(gtk.Window):
	
	## 构造函数。
	#  @param callback 响应回调函数。
	def __init__(self, callback):
		gtk.Window.__init__(self, type = gtk.WINDOW_TOPLEVEL)
		self.set_title(_('Select lyrics'))
		self.set_default_size(640, 480)
		self.set_position(gtk.WIN_POS_CENTER)
		self.connect('delete-event', self._on_delete_event)
		self._notebook = gtk.Notebook()
		self._notebook.set_scrollable(True)
		action_area = gtk.HButtonBox()
		action_area.set_layout(gtk.BUTTONBOX_END)
		action_area.set_border_width(2)
		action_area.set_spacing(2)
		btn_ok = gtk.Button(stock = gtk.STOCK_OK)
		btn_ok.connect('released', self._on_ok_released)
		action_area.pack_start(btn_ok, False, False)
		btn_cancel = gtk.Button(stock = gtk.STOCK_CANCEL)
		btn_cancel.connect('released', self._on_cancel_released)
		action_area.pack_start(btn_cancel, False, False)
		vbox = gtk.VBox()
		vbox.pack_start(self._notebook)
		vbox.pack_start(action_area, False, True)
		vbox.show_all()
		self.add(vbox)
		#
		self._callback = callback
		self._songinfo = {}
		self._candidate = {}
		self._model = {}
		self._treeview = {}
		self._selection = {}
		self._preview = {}
		return
	
	## 添加一个选择任务。
	#  @param songinfo 歌曲信息。
	#  @param candidate 候选歌词。
	def add_task(self, songinfo, candidate):
		labeltext = '%s(%d)' % (songinfo, len(candidate))
		hashid = hash(labeltext)
		if hashid in self._songinfo:
			log.warn('song already exist %s' % songinfo)
		else:
			# build widgets
			model = gtk.ListStore(int, str, str, int)
			count = 0
			for c in candidate:
				model.append([c[0], c[1].ar, c[1].ti, count])
				count = count + 1
			treeview = gtk.TreeView(model)
			treeview.set_rules_hint(True)
			treeview.append_column(gtk.TreeViewColumn('', gtk.CellRendererText(), text = 0))
			treeview.append_column(gtk.TreeViewColumn(_('Artist'), gtk.CellRendererText(), text = 1))
			treeview.append_column(gtk.TreeViewColumn(_('Title'), gtk.CellRendererText(), text = 2))
			selection = treeview.get_selection()
			selection.connect('changed', self._selection_changed)
			preview = gtk.TextView()
			preview.set_editable(False)
			preview.set_cursor_visible(False)
			# add to notebook
			label = gtk.Label(labeltext)
			panel = gtk.HPaned()
			scroll = gtk.ScrolledWindow()
			scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			scroll.add_with_viewport(treeview)
			panel.pack1(scroll, False, False)
			scroll = gtk.ScrolledWindow()
			scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			scroll.add_with_viewport(preview)
			panel.pack2(scroll, False, False)
			panel.set_position(180)
			panel.show_all()
			pageid = self._notebook.append_page(panel, label)
			self._notebook.set_tab_label_packing(panel, False, False, gtk.PACK_START)
			# store widgets handle
			self._songinfo[hashid] = songinfo
			self._candidate[hashid] = candidate
			self._model[hashid] = model
			self._treeview[hashid] = treeview
			self._selection[hashid] = selection
			self._preview[hashid] = preview
			# show up
			self._notebook.set_current_page(pageid)
			iter = model.get_iter_first()
			if iter:
				selection.select_iter(iter)
			else:
				preview.get_buffer().set_text(_('Lyrics not found'))
		return
	
	def _selection_changed(self, widget):
		pageid = self._notebook.get_current_page()
		child = self._notebook.get_nth_page(pageid)
		hashid = hash(self._notebook.get_tab_label_text(child))
		selected = widget.get_selected()
		if selected[1]:
			index = selected[0].get_value(selected[1], 3)
			self._preview[hashid].get_buffer().set_text(self._candidate[hashid][index][1].raw)
		else:
			self._preview[hashid].get_buffer().set_text('')
		return
	
	def _on_ok_released(self, button):
		if self._notebook.get_n_pages() == 1:
			self.hide()
		pageid = self._notebook.get_current_page()
		child = self._notebook.get_nth_page(pageid)
		hashid = hash(self._notebook.get_tab_label_text(child))
		song = self._songinfo[hashid]
		selected = self._selection[hashid].get_selected()
		index = selected[0].get_value(selected[1], 3)
		lyrics = self._candidate[hashid][index][1]
		self._notebook.remove_page(pageid)
		del self._preview[hashid]
		del self._selection[hashid]
		del self._treeview[hashid]
		del self._model[hashid]
		del self._candidate[hashid]
		del self._songinfo[hashid]
		self._callback(song, lyrics)
		return
	
	def _on_cancel_released(self, button):
		if self._notebook.get_n_pages() == 1:
			self.hide()
		pageid = self._notebook.get_current_page()
		child = self._notebook.get_nth_page(pageid)
		hashid = hash(self._notebook.get_tab_label_text(child))
		song = self._songinfo[hashid]
		self._notebook.remove_page(pageid)
		del self._preview[hashid]
		del self._selection[hashid]
		del self._treeview[hashid]
		del self._model[hashid]
		del self._candidate[hashid]
		del self._songinfo[hashid]
		self._callback(song, None)
		return
		
	def _on_delete_event(self, widget, event):
		self.hide()
		for pageid in range(self._notebook.get_n_pages()):
			child = self._notebook.get_nth_page(pageid)
			hashid = hash(self._notebook.get_tab_label_text(child))
			self._notebook.remove_page(pageid)
			del self._preview[hashid]
			del self._selection[hashid]
			del self._treeview[hashid]
			del self._model[hashid]
			del self._candidate[hashid]
			del self._songinfo[hashid]
		self._callback(None, None)
		return True
	
