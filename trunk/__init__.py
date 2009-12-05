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
#  RBLyrics.

import rhythmdb, rb
import os, gettext, logging, logging.handlers, sys, gtk, gtk.glade
from chooser import LyricsChooser
from prefs import Preference
from engine import Engine
from display import Display
from utils import save_lyrics, load_lyrics, open_lyrics, SongInfo
_ = gettext.gettext
log = logging.getLogger('RBLyrics')
## RBLyrics plugin.
class RBLyrics(rb.Plugin):

	## The constructor.
	def __init__(self):
		rb.Plugin.__init__(self)
		return
	
	def _on_playing_changed(self, player, playing):
		log.debug(playing)
		if playing:
			self._display.set_lyrics(self._lyrics)
			self._display.resume()
		else:
			self._display.pause()
		return
		
	## Elapsed changed handler.
	def _on_elapsed_changed(self, player, elapsed):
		if player.get_playing():
			self._display.set_lyrics(self._lyrics)
			self._display.synchronize(elapsed)
			self._display.resume()
		return
	
	## Playing song changed handler.
	def _on_playing_song_changed(self, player, entry):
		log.debug('enter')
		self._display.pause()
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
				Engine(self._prefs.get_engine(), songinfo, self._receive_lyrics).search()
		log.debug('leave')
		return
	
	## Open lyrics handler for popup menu.
	def _open_lyrics_popup(self, action):
		log.debug('enter')
		source = self._shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			self._open_lyrics(entry)
		log.debug('leave')
		return
	
	## Open lyrics handler for shortcut menu.
	def _open_lyrics_shortcut(self, action):
		log.debug('enter')
		entry = self._shell.props.shell_player.get_playing_entry ()
		if entry:
			self._open_lyrics(entry)
		log.debug('leave')
		return
	
	## Open lyrics file.
	#  @param entry Song entry to be opened.
	def _open_lyrics(self, entry):
		log.debug('enter')
		artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
		title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
		songinfo = SongInfo(artist, title)
		if not open_lyrics(self._prefs.get('main.directory'), songinfo):
			log.info('%s not found' % songinfo)
			rb.error_dialog(title = _('Lyrics not found'), message = str(songinfo))
		log.debug('leave')
		return
	
	def _chooser_handler(self, song, lyrics):
		log.debug('enter')
		if lyrics:
			save_lyrics(self._prefs.get('main.directory'), self._prefs.get('main.file_pattern'), song, lyrics)
		#
		current_song = None
		entry = self._shell.props.shell_player.get_playing_entry()
		if entry:
			artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
			current_song = SongInfo(artist, title)
		if current_song != None and song != None and current_song == song:
			self._lyrics = lyrics
			self._display.set_lyrics(lyrics)
			self._display.resume()
		log.debug('leave')
		return
		
	## Lyrics choose response hander.
	def _receive_lyrics(self, songinfo, candidate):
		log.debug('enter')
		n_candidates = len(candidate)
		log.info('%d candidates found for %s' % (n_candidates, songinfo))
		if n_candidates == 0:
			self._chooser_handler(songinfo, None)
		elif candidate[0][0] == 0:
			self._chooser_handler(songinfo, candidate[0][1])
		else:
			gtk.gdk.threads_enter()
			self._chooser.add_task(songinfo, candidate)
			self._chooser.present()
			gtk.gdk.threads_leave()
		log.debug('leave')
		return
	
	def _on_embedded_toggled(self, widget):
		if widget.get_active():
			value = 'True'
		else:
			value = 'False'
		log.debug('display.embedded = %s' % value)
		self._prefs.set('display.embedded', value)
		return
	
	def _on_gosd_toggled(self, widget):
		if widget.get_active():
			value = 'True'
		else:
			value = 'False'
		log.debug('display.gosd = %s' % value)
		self._prefs.set('display.gosd', value)
		return
	
	def _on_roller_toggled(self, widget):
		if widget.get_active():
			value = 'True'
		else:
			value = 'False'
		log.debug('display.roller = %s' % value)
		self._prefs.set('display.roller', value)
		return
	## Plugin activation.
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
		cachedir = os.path.join(rb.user_cache_dir(), 'RBLyrics')
		if not os.path.exists(cachedir):
			os.makedirs(cachedir)
		filename = os.path.join(cachedir, 'log')
		file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=102400, backupCount=0)
		file_handler.setFormatter(logging.Formatter('%(levelname)-8s %(module)s::%(funcName)s - %(message)s', '%m-%d %H:%M'))
		log.addHandler(file_handler)
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
		action = gtk.Action('OpenLyricsToolBar', _('Lyrics'), _('Open the lyrics of the playing song'), gtk.STOCK_EDIT)
		action.connect('activate', self._open_lyrics_shortcut)
		self._actiongroup.add_action(action)
		action = gtk.Action('OpenLyricsPopup', _('Lyrics'), _('Open the lyrics of the selected song'), gtk.STOCK_EDIT)
		action.connect('activate', self._open_lyrics_popup)
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
		#
		uim = shell.props.ui_manager
		uim.insert_action_group(self._actiongroup, 0)
		self._ui_id= uim.add_ui_from_file(self.find_file('ui.xml'))
		uim.ensure_update()
		self._prefs.watcher.append(self)
		log.info('activated')
		return
	
	## Plugin deactivation.
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
	
	## Configure dialog interface.
	def create_configure_dialog(self):
		self._prefs.present()
		return self._prefs
		
	def update_config(self, config):
		name = config.name
		value = config.value
		if name in ['display.embedded', 'display.gosd', 'display.roller']:
			self._action[name].set_active(value == 'True')
		return

