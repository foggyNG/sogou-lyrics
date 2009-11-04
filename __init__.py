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

import rhythmdb, rb
import os, gettext, logging, logging.handlers, sys, gtk

from Preference import Preference
from LyricsChooser import LyricsChooser
from Engine import Engine
from DisplayOSD import DisplayOSD
from utils import *
_ = gettext.gettext

class RBLyrics(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)
		return
		
	def __elapsed_changed_handler(self, player, playing):
		if playing and self.__lyrics != None:
			elapsed = player.get_playing_time()
			line = self.__lyrics.get_line(elapsed)
			if line != None:
				self.__display.show(line)
		return
	
	def __receive_lyrics(self, songinfo, candidate):
		log.debug('enter')
		n_candidates = len(candidate)
		if n_candidates == 0:
			self.__display.show(_('%s not found') % songinfo)
		elif candidate[0][0] == 0:
			log.info('%s prepared' % songinfo)
			self.__display.show(_('%s prepared') % songinfo)
			self.__lyrics = candidate[0][1]
			save_lyrics(self.__prefs.get('folder'), songinfo, self.__lyrics)
		else:
			log.info('%d candidates found for %s' % (n_candidates, songinfo))
			self.__chooser.set_instance(songinfo, candidate)
			self.__chooser.show()
		log.debug('leave')
		return
	
	def __playing_song_changed_handler(self, player, entry):
		log.debug('enter')
		if entry:
			# get playing song properties		
			artist = self.__db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self.__db.entry_get(entry, rhythmdb.PROP_TITLE)
			songinfo = SongInfo(artist, title)
			log.info(songinfo)
			self.__lyrics = load_lyrics(self.__prefs.get('folder'), songinfo)
			if self.__lyrics != None:
				self.__display.show(_('%s prepared') % songinfo)
			elif self.__prefs.get('download'):
				self.__display.show(_('%s downloading') % songinfo)
				candidate = Engine(self.__prefs.get('engine'), songinfo).get_lyrics()
				self.__receive_lyrics(songinfo, candidate)
			else:
				self.__display.show(_('%s not found') % songinfo)
		log.debug('leave')
		return

	def __open_lyrics_popup(self, action):
		log.debug('enter')
		source = self.__shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			self.__open_lyrics(entry)
		log.debug('leave')
		return
	
	def __open_lyrics_shortcut(self, action):
		log.debug('enter')
		entry = self.__player.get_playing_entry ()
		if entry:
			self.__open_lyrics(entry)
		log.debug('leave')
		return
	
	def __open_lyrics(self, entry):
		log.debug('enter')
		artist = self.__db.entry_get(entry, rhythmdb.PROP_ARTIST)
		title = self.__db.entry_get(entry, rhythmdb.PROP_TITLE)
		songinfo = SongInfo(artist, title)
		if not open_lyrics(self.__prefs.get('folder'), songinfo):
			log.info('%s not found' % songinfo)
			message = _('Artist:\t%s\nTitle:\t%s\nLyrics not found!') % (artist, title)
			dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=message)
			dlg.set_title(_(APP_NAME))
			dlg.run()
			dlg.destroy()
		log.debug('leave')
		return
	
	def __chooser_response_handler(self, songinfo, lyrics):
		log.debug('enter')
		is_current = False
		entry = self.__player.get_playing_entry()
		if entry:
			artist = self.__db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self.__db.entry_get(entry, rhythmdb.PROP_TITLE)
			songinfo_t = SongInfo(artist, title)
			if songinfo == songinfo_t:
				is_current = True
		#
		if lyrics:
			save_lyrics(self.__prefs.get('folder'), songinfo, lyrics)
			if is_current:
				self.__display.show(_('%s prepared') % songinfo)
				self.__lyrics = lyrics
		else:
			if is_current:
				self.__display.show(_('%s not found') % songinfo)
		log.debug('leave')
		return
		
	def activate(self, shell):
		# internationalization
		LOCALE_DIR = self.find_file('locale')
		for module in (gettext, gtk.glade):
			module.bindtextdomain(APP_NAME, LOCALE_DIR)
			module.textdomain(APP_NAME)
		gettext.install(APP_NAME)
		# logging
		filename = os.path.join(os.path.dirname(LOCALE_DIR), 'log')
		file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=102400, backupCount=0)
		file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(module)s::%(funcName)s - %(message)s', '%m-%d %H:%M'))
		log.addHandler(file_handler)
		# checkout python version
		version = sys.version_info
		if version[0] != 2 or version[1] < 6:
			log.critical(sys.version)
		#
		self.__prefs = Preference(self.find_file('prefs.glade'))
		self.__display = DisplayOSD(self.__prefs)
		if not os.path.exists(self.__prefs.get('folder')):
			os.mkdir(self.__prefs.get('folder'))
		self.__chooser = LyricsChooser(self.find_file('lyrics-chooser.glade'), self.__chooser_response_handler)
		self.__lyrics = None
		self.__shell = shell
		self.__player = shell.get_player()
		self.__db = shell.get_property('db')
		self.__handler = [
			self.__player.connect('playing-song-changed', self.__playing_song_changed_handler),
			self.__player.connect('elapsed-changed', self.__elapsed_changed_handler)]
		#
		self.__action = [
			gtk.Action('OpenLyricsToolBar', _('Lyrics'), _('Open the lyrics of the playing song'), 'RBLyrics'),
			gtk.Action('OpenLyricsPopup', _('Lyrics'), _('Open the lyrics of the selected song'), 'RBLyrics')]
			#gtk.Action('OpenLyricsMenuBar', _('Open Playing Lyrics'), _('Open the lyrics of the playing song'), 'RBLyrics')]
		self.__action[0].connect('activate', self.__open_lyrics_shortcut)
		self.__action[1].connect('activate', self.__open_lyrics_popup)
		#self.action[2].connect('activate', self.__open_lyrics_shortcut)
		self.__actiongroup = gtk.ActionGroup('RBLyricsActions')
		self.__actiongroup.add_action(self.__action[0])
		self.__actiongroup.add_action(self.__action[1])
		#self.__actiongroup.add_action_with_accel (self.action[2], "<control>L")
		
		# add icon
		iconsource = gtk.IconSource()
		iconsource.set_filename(self.find_file("open-lyrics.svg"))
		iconset = gtk.IconSet()
		iconset.add_source(iconsource)
		iconfactory = gtk.IconFactory()
		iconfactory.add(APP_NAME, iconset)
		iconfactory.add_default()
		#
		uim = shell.get_ui_manager()
		uim.insert_action_group(self.__actiongroup, 0)
		self.__ui_id= uim.add_ui_from_file(self.find_file('ui.xml'))
		uim.ensure_update()
		log.info('activated')
		return

	def deactivate(self, shell):
		for handler in self.__handler:
			self.__player.disconnect(handler)
		uim = shell.get_ui_manager()
		uim.remove_ui(self.__ui_id)
		uim.remove_action_group(self.__actiongroup)
		uim.ensure_update()
		for action in self.__action:
			del action
		del self.__actiongroup
		del self.__action
		del self.__handler
		del self.__db
		del self.__player
		del self.__shell
		del self.__lyrics
		del self.__chooser
		del self.__display
		del self.__prefs
		log.info('deactivated')
		return

	def create_configure_dialog(self):
		dialog = self.__prefs.get_dialog()
		dialog.present()
		return dialog

