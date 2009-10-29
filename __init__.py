#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os, ClientCookie, urllib2, re, logging
import rhythmdb, rb
import gobject, gtk, gconf
from Preference import Preference
from LyricsChooser import LyricsChooser
from Song import *
from Engine import Engine
from DisplayOSD import DisplayOSD

class RBLyrics(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)
		return
		
	def elapsed_changed_handler(self, player, playing):
		if playing:
			elapsed = player.get_playing_time()
			if self.song_.load_lyrics():
				try:
					self.display_.show(self.song_.lrc_[elapsed])
				except KeyError:
					pass
		return
	
	def receive_lyrics(self, lyrics, song):
		logging.debug('enter')
		n_candidates = len(lyrics)
		if n_candidates == 0:
			self.display_.show('(%s - %s) not found' % (song.songinfo_['ar'], song.songinfo_['ti']))
		elif lyrics[0].edit_distance_ == 0:
			logging.info('(%s - %s) prepared' % (song.songinfo_['ar'], song.songinfo_['ti']))
			self.display_.show('(%s - %s) prepared' % (song.songinfo_['ar'], song.songinfo_['ti']))
			lyrics[0].save()
		else:
			logging.info('%d candidates found for (%s - %s)' % (n_candidates, song.songinfo_['ar'], song.songinfo_['ti']))
			self.chooser_.set_instance(lyrics, song)
			self.chooser_.show()
		logging.debug('leave')
		return
	
	def playing_song_changed_handler(self, player, entry):
		logging.debug('enter')
		if entry:
			# get playing song properties		
			artist = self.db_.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self.db_.entry_get(entry, rhythmdb.PROP_TITLE)
			logging.info('%s - %s' % (artist, title))
			#
			self.song_ = init_song_search(self.prefs_, artist, title)
			if self.song_.load_lyrics():
				self.display_.show('(%s - %s) prepared' % (artist, title))
			elif self.prefs_.get('download'):
				self.display_.show('(%s - %s) downloading' % (artist, title))
				lyrics = Engine(self.prefs_.get('engine'), self.song_).get_lyrics()
				self.receive_lyrics(lyrics, self.song_)
			else:
				self.display_.show('(%s - %s) not found' % (artist, title))
		logging.debug('leave')
		return

	def open_lyrics_popup(self, action):
		logging.debug('enter')
		source = self.shell_.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			self.open_lyrics_file(entry)
		logging.debug('leave')
		return
	
	def open_lyrics_shortcut(self, action):
		logging.debug('enter')
		entry = self.player_.get_playing_entry ()
		if entry:
			self.open_lyrics_file(entry)
		logging.debug('leave')
		return
	
	def open_lyrics_file(self, entry):
		logging.debug('enter')
		ret = False
		artist = self.db_.entry_get(entry, rhythmdb.PROP_ARTIST)
		title = self.db_.entry_get(entry, rhythmdb.PROP_TITLE)
		song = init_song_search(self.prefs_, artist, title)
		if not song.open_lyrics_file():
			logging.info('lyrics not found (%s - %s)' % (artist, title))
			message = 'Artist:\t%s\nTitle:\t%s\nLyrics not found!' % (artist, title)
			dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=message)
			dlg.set_title('Open Lyrics')
			dlg.run()
			dlg.destroy()	
		logging.debug('leave %s' % ret)
		return ret
	
	def activate(self, shell):
		# logging
		logging.basicConfig(level=logging.INFO, format= 'RBLyrics %(levelname)-8s %(module)s::%(funcName)s - %(message)s')
		self.prefs_ = Preference(self.find_file('prefs.glade'))
		if not os.path.exists(self.prefs_.get('folder')):
			os.mkdir(self.prefs_.get_pref('folder'))
		self.chooser_ = LyricsChooser(self.find_file('lyrics-chooser.glade'))
		self.song_ = None
		self.display_ = DisplayOSD()
		self.shell_ = shell
		self.player_ = shell.get_player()
		self.db_ = shell.get_property('db')
		self.handler_ = [
			self.player_.connect('playing-song-changed', self.playing_song_changed_handler),
			self.player_.connect('elapsed-changed', self.elapsed_changed_handler)]
		#
		self.action_ = [
			gtk.Action('OpenLyricsToolBar', _('Lyrics'), _('Open the lyrics of the playing song'), 'RBLyrics'),
			gtk.Action('OpenLyricsPopup', _('Open Lyrics'), _('Open the lyrics of the selected song'), 'RBLyrics')]
			#gtk.Action('OpenLyricsMenuBar', _('Open Playing Lyrics'), _('Open the lyrics of the playing song'), 'RBLyrics')]
		self.action_[0].connect('activate', self.open_lyrics_shortcut)
		self.action_[1].connect('activate', self.open_lyrics_popup)
		#self.action[2].connect('activate', self.open_lyrics_shortcut)
		self.action_group_ = gtk.ActionGroup('RBLyricsActions')
		self.action_group_.add_action(self.action_[0])
		self.action_group_.add_action(self.action_[1])
		#self.action_group.add_action_with_accel (self.action[2], "<control>L")
		
		# add icon
		iconsource = gtk.IconSource()
		iconsource.set_filename(self.find_file("open-lyrics.svg"))
		iconset = gtk.IconSet()
		iconset.add_source(iconsource)
		iconfactory = gtk.IconFactory()
		iconfactory.add("RBLyrics", iconset)
		iconfactory.add_default()
		#
		uim = shell.get_ui_manager()
		uim.insert_action_group(self.action_group_, 0)
		self.ui_id_= uim.add_ui_from_file(self.find_file('ui.xml'))
		uim.ensure_update()
		logging.info('Sogou Lyrics activated')
		return

	def deactivate(self, shell):
		for handler in self.handler_:
			self.player_.disconnect(handler)
		uim = shell.get_ui_manager()
		uim.remove_ui (self.ui_id_)
		uim.remove_action_group (self.action_group_)
		uim.ensure_update()
		for action in self.action_:
			del action
		#
		del self.display_
		del self.song_
		del self.prefs_
		del self.chooser_
		del self.player_
		del self.db_
		del self.shell_
		del self.handler_
		del self.action_group_
		del self.action_
		logging.info('Sogou Lyrics deactivated')
		return

	def create_configure_dialog(self):
		dialog = self.prefs_.get_dialog()
		dialog.present()
		return dialog

