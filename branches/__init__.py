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
import os, gettext, logging, logging.handlers, sys, gtk, gtk.glade, gtk.gdk, pango
_ = gettext.gettext

from chooser import LyricsChooser
from prefs import Preference
from engine import Engine
from display import Display
from utils import *

## RBLyrics plugin.
class RBLyrics(rb.Plugin):

	## The constructor.
	def __init__(self):
		rb.Plugin.__init__(self)
		return
	
	## Elapsed changed handler.
	def _on_elapsed_changed(self, player, elapsed):
		elapsed = player.get_playing_time()
		self._display.interface().synchronize(elapsed)
		return
	
	def _on_playing_changed(self, player, playing):
		if playing:
			self._display.interface().resume()
			self._display.show()
		else:
			self._display.interface().pause()
			self._display.hide()
		return
	## Playing song changed handler.
	def _on_playing_song_changed(self, player, entry):
		log.debug('enter')
		self._display.interface().pause()
		if entry:
			# get playing song properties		
			artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
			songinfo = SongInfo(artist, title)
			log.info(songinfo)
			lyrics = load_lyrics(self._prefs.get('main.directory'), songinfo)
			if lyrics:
				self._display.interface().set_lyrics(lyrics)
				self._display.interface().resume()
			elif self._prefs.get('main.download') == 'True':
				Engine(self._prefs, songinfo, self._receive_lyrics).start()
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
			message = _('Artist:\t%s\nTitle:\t%s\nLyrics not found!') % (artist, title)
			dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=message)
			dlg.set_title(_('RBLyrics'))
			dlg.run()
			dlg.destroy()
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
			self._display.interface().set_lyrics(lyrics)
			self._display.interface().resume()
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
	
	## Plugin activation.
	def activate(self, shell):
		# internationalization
		LOCALE_DIR = self.find_file('locale')
		for module in (gettext, gtk.glade):
			module.bindtextdomain('RBLyrics', LOCALE_DIR)
			module.textdomain('RBLyrics')
		gettext.install('RBLyrics')
		# logging
		log.setLevel(logging.INFO)
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
		# checkout python version
		version = sys.version_info
		if version[0] != 2 or version[1] < 6:
			log.critical(sys.version)
		#
		self._prefs = Preference()
		self._display = Display(self._prefs)
		if not os.path.exists(self._prefs.get('main.directory')):
			os.mkdir(self._prefs.get('main.directory'))
		self._shell = shell
		self._handler = [
			self._shell.props.shell_player.connect('playing-song-changed', self._on_playing_song_changed),
			self._shell.props.shell_player.connect('elapsed-changed', self._on_elapsed_changed),
			self._shell.props.shell_player.connect('playing-changed', self._on_playing_changed)]
		#
		self._action = [
			gtk.Action('OpenLyricsToolBar', _('Lyrics'), _('Open the lyrics of the playing song'), 'RBLyrics'),
			gtk.Action('OpenLyricsPopup', _('Lyrics'), _('Open the lyrics of the selected song'), 'RBLyrics')]
			#gtk.Action('OpenLyricsMenuBar', _('Open Playing Lyrics'), _('Open the lyrics of the playing song'), 'RBLyrics')]
		self._action[0].connect('activate', self._open_lyrics_shortcut)
		self._action[1].connect('activate', self._open_lyrics_popup)
		#self.action[2].connect('activate', self._open_lyrics_shortcut)
		self._actiongroup = gtk.ActionGroup('RBLyricsActions')
		self._actiongroup.add_action(self._action[0])
		self._actiongroup.add_action(self._action[1])
		#self._actiongroup.add_action_with_accel (self.action[2], "<control>L")
		
		# add icon
		iconsource = gtk.IconSource()
		iconsource.set_filename(self.find_file("RBLyrics.svg"))
		iconset = gtk.IconSet()
		iconset.add_source(iconsource)
		iconfactory = gtk.IconFactory()
		iconfactory.add('RBLyrics', iconset)
		iconfactory.add_default()
		#
		uim = shell.props.ui_manager
		uim.insert_action_group(self._actiongroup, 0)
		self._ui_id= uim.add_ui_from_file(self.find_file('ui.xml'))
		uim.ensure_update()
		#
		self._chooser = LyricsChooser(self._chooser_handler)
		#
		'''self._embedded = gtk.Label('lyrics')
		self._embedded.modify_font(pango.FontDescription(self._prefs.get('display.font')))
		self._embedded.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(self._prefs.get('display.color')))
		shell.add_widget (self._embedded, rb.SHELL_UI_LOCATION_MAIN_TOP)
		self._embedded.show()'''
		log.info('activated')
		return
	
	## Plugin deactivation.
	def deactivate(self, shell):
		del self._chooser
		for handler in self._handler:
			self._shell.props.shell_player.disconnect(handler)
		uim = shell.props.ui_manager
		uim.remove_ui(self._ui_id)
		uim.remove_action_group(self._actiongroup)
		uim.ensure_update()
		for action in self._action:
			del action
		del self._actiongroup
		del self._action
		del self._handler
		del self._shell
		del self._display
		del self._prefs
		log.info('deactivated')
		return
	
	## Configure dialog interface.
	def create_configure_dialog(self):
		self._prefs.present()
		return self._prefs

