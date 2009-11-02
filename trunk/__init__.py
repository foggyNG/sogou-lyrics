#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, urllib2, re, logging, gettext
import rhythmdb, rb
import gobject, gtk, gconf
from Preference import Preference
from LyricsChooser import LyricsChooser
from Song import *
from Engine import Engine
from DisplayOSD import DisplayOSD
_ = gettext.gettext

class RBLyrics(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)
		return
		
	def __elapsed_changed_handler(self, player, playing):
		if playing:
			elapsed = player.get_playing_time()
			try:
				self.__display.show(self.__song.lrc_[elapsed])
			except KeyError:
				pass
		return
	
	def __receive_lyrics(self, lyrics, song):
		logging.debug('enter')
		n_candidates = len(lyrics)
		if n_candidates == 0:
			self.__display.show(_('(%s - %s) not found') % (song.songinfo_['ar'], song.songinfo_['ti']))
		elif lyrics[0].edit_distance_ == 0:
			logging.info('(%s - %s) prepared' % (song.songinfo_['ar'], song.songinfo_['ti']))
			self.__display.show(_('(%s - %s) prepared') % (song.songinfo_['ar'], song.songinfo_['ti']))
			lyrics[0].save_lyrics()
			self.__song = lyrics[0]
		else:
			logging.info('%d candidates found for (%s - %s)' % (n_candidates, song.songinfo_['ar'], song.songinfo_['ti']))
			self.__chooser.set_instance(lyrics, song)
			self.__chooser.show()
		logging.debug('leave')
		return
	
	def __playing_song_changed_handler(self, player, entry):
		logging.debug('enter')
		if entry:
			# get playing song properties		
			artist = self.__db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self.__db.entry_get(entry, rhythmdb.PROP_TITLE)
			logging.info('(%s - %s)' % (artist, title))
			#
			self.__song = init_song_search(self.__prefs, artist, title)
			if self.__song.load_lyrics():
				self.__display.show(_('(%s - %s) prepared') % (artist, title))
			elif self.__prefs.get('download'):
				self.__display.show(_('(%s - %s) downloading') % (artist, title))
				lyrics = Engine(self.__prefs.get('engine'), self.__song).get_lyrics()
				self.__receive_lyrics(lyrics, self.__song)
			else:
				self.__display.show(_('(%s - %s) not found') % (artist, title))
		logging.debug('leave')
		return

	def __open_lyrics_popup(self, action):
		logging.debug('enter')
		source = self.__shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			self.__open_lyrics(entry)
		logging.debug('leave')
		return
	
	def __open_lyrics_shortcut(self, action):
		logging.debug('enter')
		entry = self.__player.get_playing_entry ()
		if entry:
			self.__open_lyrics(entry)
		logging.debug('leave')
		return
	
	def __open_lyrics(self, entry):
		logging.debug('enter')
		artist = self.__db.entry_get(entry, rhythmdb.PROP_ARTIST)
		title = self.__db.entry_get(entry, rhythmdb.PROP_TITLE)
		song = init_song_search(self.__prefs, artist, title)
		if not song.open_lyrics():
			logging.info('(%s - %s) not found' % (artist, title))
			message = _('Artist:\t%s\nTitle:\t%s\nLyrics not found!') % (artist, title)
			dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=message)
			dlg.set_title(_('RBLyrics'))
			dlg.run()
			dlg.destroy()	
		logging.debug('leave')
		return
	
	def __chooser_response_handler(self, song):
		logging.debug('enter')
		self.__song.load_lyrics()
		logging.debug('leave')
		return
		
	def activate(self, shell):
		# internationalization
		APP_NAME = 'RBLyrics'
		LOCALE_DIR = self.find_file('locale')
		for module in (gettext, gtk.glade):
			module.bindtextdomain(APP_NAME, LOCALE_DIR)
			module.textdomain(APP_NAME)
		gettext.install(APP_NAME)
		# logging
		logging.basicConfig(level=logging.DEBUG, format= 'RBLyrics %(levelname)-8s %(module)s::%(funcName)s - %(message)s')
		self.__prefs = Preference(self.find_file('prefs.glade'))
		self.__display = DisplayOSD(self.__prefs)
		if not os.path.exists(self.__prefs.get('folder')):
			os.mkdir(self.__prefs.get('folder'))
		self.__chooser = LyricsChooser(self.find_file('lyrics-chooser.glade'), self.__chooser_response_handler)
		self.__song = None
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
		logging.info('activated')
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
		del self.__song
		del self.__chooser
		del self.__display
		del self.__prefs
		logging.info('deactivated')
		return

	def create_configure_dialog(self):
		dialog = self.__prefs.get_dialog()
		dialog.present()
		return dialog

