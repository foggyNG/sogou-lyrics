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
import os, gettext, logging, logging.handlers, sys, gtk
_ = gettext.gettext

from prefs import Preference
from chooser import LyricsChooser
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
	def _elapsed_changed_handler(self, player, playing):
		if playing and self._lyrics != None:
			elapsed = player.get_playing_time()
			line = self._lyrics.get_line(elapsed)
			if line != None:
				self._display.show(line)
		return
	
	## Receive lyrics from search engine.
	#  @param songinfo Song information.
	#  @param candidate Lyrics candidates.
	def _receive_lyrics(self, songinfo, candidate):
		log.debug('enter')
		n_candidates = len(candidate)
		if n_candidates == 0:
			self._display.show(_('%s not found') % songinfo)
		elif candidate[0][0] == 0:
			self._display.show(_('%s prepared') % songinfo)
			self._lyrics = candidate[0][1]
			save_lyrics(self._prefs.get('folder'), songinfo, self._lyrics)
		elif not self._prefs.get('choose'):
			self._display.show(_('%s not found') % songinfo)
		else:
			self._chooser.set_instance(songinfo, candidate)
			self._chooser.show()
		log.debug('leave')
		return
	
	## Playing song changed handler.
	def _playing_song_changed_handler(self, player, entry):
		log.debug('enter')
		if entry:
			# get playing song properties		
			artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
			songinfo = SongInfo(artist, title)
			log.info(songinfo)
			self._lyrics = load_lyrics(self._prefs.get('folder'), songinfo)
			if self._lyrics != None:
				self._display.show(_('%s prepared') % songinfo)
			elif self._prefs.get('download'):
				self._display.show(_('%s downloading') % songinfo)
				candidate = Engine(self._prefs.get('engine'), songinfo).get_lyrics()
				self._receive_lyrics(songinfo, candidate)
			else:
				self._display.show(_('%s not found') % songinfo)
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
		if not open_lyrics(self._prefs.get('folder'), songinfo):
			log.info('%s not found' % songinfo)
			message = _('Artist:\t%s\nTitle:\t%s\nLyrics not found!') % (artist, title)
			dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=message)
			dlg.set_title(_(APP_NAME))
			dlg.run()
			dlg.destroy()
		log.debug('leave')
		return
	
	## Lyrics choose response hander.
	def _chooser_response_handler(self, songinfo, lyrics):
		log.debug('enter')
		is_current = False
		entry = self._shell.props.shell_player.get_playing_entry()
		if entry:
			artist = self._shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self._shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
			songinfo_t = SongInfo(artist, title)
			if songinfo == songinfo_t:
				is_current = True
		#
		if lyrics:
			save_lyrics(self._prefs.get('folder'), songinfo, lyrics)
			if is_current:
				self._display.show(_('%s prepared') % songinfo)
				self._lyrics = lyrics
		else:
			if is_current:
				self._display.show(_('%s not found') % songinfo)
		log.debug('leave')
		return
	
	## Plugin activation.
	def activate(self, shell):
		# internationalization
		LOCALE_DIR = self.find_file('locale')
		for module in (gettext, gtk.glade):
			module.bindtextdomain(APP_NAME, LOCALE_DIR)
			module.textdomain(APP_NAME)
		gettext.install(APP_NAME)
		# logging
		log.setLevel(logging.DEBUG)
		console_handler = logging.StreamHandler()
		console_handler.setLevel(logging.INFO)
		console_handler.setFormatter(logging.Formatter('RBLyrics %(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
		log.addHandler(console_handler)
		cachedir = os.path.join(rb.user_cache_dir(), APP_NAME)
		if not os.path.exists(cachedir):
			os.makedirs(cachedir)
		filename = os.path.join(cachedir, 'log')
		file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=102400, backupCount=0)
		file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(module)s::%(funcName)s - %(message)s', '%m-%d %H:%M'))
		log.addHandler(file_handler)
		# checkout python version
		version = sys.version_info
		if version[0] != 2 or version[1] < 6:
			log.critical(sys.version)
		#
		self._prefs = Preference(self.find_file('prefs.glade'))
		self._display = Display(self._prefs)
		if not os.path.exists(self._prefs.get('folder')):
			os.mkdir(self._prefs.get('folder'))
		self._chooser = LyricsChooser(self.find_file('chooser.glade'), self._chooser_response_handler)
		self._lyrics = None
		self._shell = shell
		self._handler = [
			self._shell.props.shell_player.connect('playing-song-changed', self._playing_song_changed_handler),
			self._shell.props.shell_player.connect('elapsed-changed', self._elapsed_changed_handler)]
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
		iconfactory.add(APP_NAME, iconset)
		iconfactory.add_default()
		#
		uim = shell.props.ui_manager
		uim.insert_action_group(self._actiongroup, 0)
		self._ui_id= uim.add_ui_from_file(self.find_file('ui.xml'))
		uim.ensure_update()
		log.info('activated')
		return
	
	## Plugin deactivation.
	def deactivate(self, shell):
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
		del self._lyrics
		del self._chooser
		del self._display
		del self._prefs
		log.info('deactivated')
		return
	
	## Configure dialog interface.
	def create_configure_dialog(self):
		dialog = self._prefs.get_dialog()
		dialog.present()
		return dialog

