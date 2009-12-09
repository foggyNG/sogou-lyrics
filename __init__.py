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

## @package RBLyrics
#  鲁班歌词。

import rhythmdb, rb
import os, gettext, logging, logging.handlers, sys, gtk, gtk.glade
from chooser import LyricsChooser
from prefs import Preference
from engine import Engine
from display import Display
from utils import save_lyrics, load_lyrics, open_lyrics, SongInfo
_ = gettext.gettext
log = logging.getLogger('RBLyrics')

## 鲁班歌词。
class RBLyrics(rb.Plugin):

	## 构造函数。
	def __init__(self):
		rb.Plugin.__init__(self)
		return
	
	## "playing-changed"事件处理函数。
	def _on_playing_changed(self, player, playing):
		if playing:
			self._display.set_lyrics(self._lyrics)
			self._display.resume()
		else:
			self._display.pause()
		return
		
	## "elapsed-changed"事件处理函数。
	def _on_elapsed_changed(self, player, elapsed):
		if player.get_playing():
			self._display.set_lyrics(self._lyrics)
			self._display.synchronize(elapsed)
			self._display.resume()
		return
	
	## "playing-song-changed"事件处理函数。
	def _on_playing_song_changed(self, player, entry):
		#self._display.pause()
		self._lyrics = None
		self._display.set_lyrics(None)
		if entry:
			# get playing song properties		
			artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
			songinfo = SongInfo(artist, title)
			log.info(songinfo)
			self._lyrics = load_lyrics(self._prefs.get('main.directory'), songinfo)
			if self._lyrics:
				self._display.set_lyrics(self._lyrics)
				self._display.resume()
			elif self._prefs.get('main.download') == 'True':
				Engine(self._prefs.get_engine(), songinfo, self._on_lyrics_arrive, True).search()
		return
	
	## 右键菜单编辑歌词事件处理函数。
	def _on_lyrics_popup_activated(self, action):
		source = self._shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			self._open_lyrics(entry)
		return
	
	## 工具栏打开歌词事件处理函数。
	def _on_lyrics_shortcut_activated(self, action):
		entry = self._shell.props.shell_player.get_playing_entry ()
		if entry:
			self._open_lyrics(entry)
		return
	
	## 右键菜单手动下载歌词事件处理函数。
	def _on_download_activated(self, action):
		source = self._shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
			songinfo = SongInfo(artist, title)
			Engine(self._prefs.get_engine(), songinfo, self._on_lyrics_arrive, False).search()
		return
		
	## 打开歌词文件。
	#  @param entry 歌曲条目。
	def _open_lyrics(self, entry):
		artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
		title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
		songinfo = SongInfo(artist, title)
		if not open_lyrics(self._prefs.get('main.directory'), songinfo):
			log.info('%s not found' % songinfo)
			rb.error_dialog(title = _('Lyrics not found'), message = str(songinfo))
		return
	
	## 歌词选择对话框响应函数。
	#  @param song 歌曲信息。
	#  @param lyrics 歌词信息。
	def _chooser_handler(self, song, lyrics):
		if lyrics:
			save_lyrics(self._prefs.get('main.directory'), self._prefs.get('main.file_pattern'), song, lyrics)
			current_song = None
			entry = self._shell.props.shell_player.get_playing_entry()
			if entry:
				artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
				title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
				current_song = SongInfo(artist, title)
			if current_song and song and current_song == song:
				self._lyrics = lyrics
				self._display.set_lyrics(lyrics)
				self._display.resume()
		return
		
	## 歌词下载模块响应函数。
	#  @param songinfo 歌曲信息。
	#  @param candidate 候选歌词。
	#  @param auto 是否自动选择歌词。
	def _on_lyrics_arrive(self, songinfo, candidate, auto):
		n_candidates = len(candidate)
		log.debug('%d candidates found for %s' % (n_candidates, songinfo))
		if auto:
			if n_candidates == 0:
				self._chooser_handler(songinfo, None)
			elif candidate[0][0] == 0:
				self._chooser_handler(songinfo, candidate[0][1])
			else:
				self._chooser.add_task(songinfo, candidate)
				self._chooser.present()
		else:
			self._chooser.add_task(songinfo, candidate)
			self._chooser.present()
		return
	
	def _on_embedded_toggled(self, widget):
		if widget.get_active():
			value = 'True'
		else:
			value = 'False'
		self._prefs.set('display.embedded', value)
		return
	
	def _on_gosd_toggled(self, widget):
		if widget.get_active():
			value = 'True'
		else:
			value = 'False'
		self._prefs.set('display.gosd', value)
		return
	
	def _on_roller_toggled(self, widget):
		if widget.get_active():
			value = 'True'
		else:
			value = 'False'
		self._prefs.set('display.roller', value)
		return
		
	def _on_single_toggled(self, widget):
		if widget.get_active():
			value = 'True'
		else:
			value = 'False'
		self._prefs.set('display.single', value)
		return
		
	## 开启插件。
	def activate(self, shell):
		# internationalization
		LOCALE_DIR = self.find_file('locale')
		for module in (gettext, gtk.glade):
			module.bindtextdomain('RBLyrics', LOCALE_DIR)
			module.textdomain('RBLyrics')
		gettext.install('RBLyrics')
		# logging
		log.setLevel(logging.DEBUG)
		console_handler = logging.StreamHandler()
		console_handler.setLevel(logging.DEBUG)
		console_handler.setFormatter(logging.Formatter('RBLyrics %(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
		log.addHandler(console_handler)
		#
		log.info(sys.version)
		#
		self._prefs = Preference()
		self._display = Display(shell, self._prefs)
		self._chooser = LyricsChooser(self._chooser_handler)
		self._lyrics = None
		if not os.path.exists(self._prefs.get('main.directory')):
			os.mkdir(self._prefs.get('main.directory'))
		self._shell = shell
		self._handler = [
			self._shell.props.shell_player.connect('playing-song-changed', self._on_playing_song_changed),
			self._shell.props.shell_player.connect('elapsed-changed', self._on_elapsed_changed),
			self._shell.props.shell_player.connect('playing-changed', self._on_playing_changed)]
		#
		self._action = {}
		self._actiongroup = gtk.ActionGroup('RBLyricsActions')
		action = gtk.Action('OpenLyricsToolBar', _('Lyrics'), _('Open lyrics of the playing song'), gtk.STOCK_EDIT)
		action.connect('activate', self._on_lyrics_shortcut_activated)
		self._actiongroup.add_action(action)
		action = gtk.Action('OpenLyricsPopup', _('Edit Lyrics'), None, gtk.STOCK_EDIT)
		action.connect('activate', self._on_lyrics_popup_activated)
		self._actiongroup.add_action(action)
		action = gtk.Action('download-lyrics', _('Download Lyrics Manually'), None, gtk.STOCK_FIND)
		action.connect('activate', self._on_download_activated)
		self._actiongroup.add_action(action)
		action = gtk.ToggleAction('rblyrics-embedded', _('RBLyrics.Embedded'), None, None)
		action.set_active(self._prefs.get('display.embedded') == 'True')
		action.connect('toggled', self._on_embedded_toggled)
		self._action['display.embedded'] = action
		self._actiongroup.add_action(action)
		action = gtk.ToggleAction('rblyrics-gosd', _('RBLyrics.OSD'), None, None)
		action.set_active(self._prefs.get('display.gosd') == 'True')
		action.connect('toggled', self._on_gosd_toggled)
		self._action['display.gosd'] = action
		self._actiongroup.add_action(action)
		action = gtk.ToggleAction('rblyrics-roller', _('RBLyrics.Roller'), None, None)
		action.set_active(self._prefs.get('display.roller') == 'True')
		action.connect('toggled', self._on_roller_toggled)
		self._action['display.roller'] = action
		self._actiongroup.add_action(action)
		action = gtk.ToggleAction('rblyrics-single', _('RBLyrics.Single'), None, None)
		action.set_active(self._prefs.get('display.single') == 'True')
		action.connect('toggled', self._on_single_toggled)
		self._action['display.single'] = action
		self._actiongroup.add_action(action)
		#
		uim = shell.props.ui_manager
		uim.insert_action_group(self._actiongroup, 0)
		self._ui_id= uim.add_ui_from_file(self.find_file('ui.xml'))
		uim.ensure_update()
		self._prefs.watcher.append(self)
		log.info('activated')
		return
	
	## 关闭插件。
	def deactivate(self, shell):
		self._prefs.watcher.remove(self)
		for handler in self._handler:
			self._shell.props.shell_player.disconnect(handler)
		uim = shell.props.ui_manager
		uim.remove_ui(self._ui_id)
		uim.remove_action_group(self._actiongroup)
		uim.ensure_update()
		del self._actiongroup
		del self._action
		del self._handler
		del self._shell
		del self._chooser
		self._display.finialize()
		del self._display
		del self._lyrics
		del self._prefs
		log.info('deactivated')
		for handler in log.handlers:
			log.removeHandler(handler)
		return
	
	## 打开首选项配置对话框。
	def create_configure_dialog(self):
		self._prefs.present()
		return self._prefs
	
	## 更新配置。
	#  @param config 待更新的配置项。
	def update_config(self, config):
		name = config.name
		value = config.value
		if name in ['display.embedded', 'display.gosd', 'display.roller', 'display.single']:
			self._action[name].set_active(value == 'True')
		return

