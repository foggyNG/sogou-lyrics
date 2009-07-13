import os, ClientCookie, urllib2, re, logging
import rhythmdb, rb
from gnomeosd import eventbridge
import gobject, gtk, gconf
from Preference import Preference
from LyricsChooser import LyricsChooser
from utils import *
from Grabber import Grabber

MESSAGE_TEMPLATE = "<message id='SogouLyrics' animations='%s' osd_fake_translucent_bg='off' drop_shadow='off' osd_vposition='%s' osd_halignment='%s'  hide_timeout='20000'><span size='20000' foreground='%s'>%s</span></message>"

class SogouLyrics(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)

	def osd_display(self, message):
		if self.prefs.get_pref('display'):
			code = MESSAGE_TEMPLATE % (self.prefs.get_pref('animation'), self.prefs.get_pref('vpos'), self.prefs.get_pref('halign'), self.prefs.get_pref('fgcolor'), message)
			self.osd.send(code)
		
	def elapsed_changed_handler(self, player, playing):
		if playing:
			elapsed = player.get_playing_time()
			if self.lrc == {} and self.load_round % 5 == 0:
				entry = self.player.get_playing_entry ()
				artist = self.db.entry_get(entry, rhythmdb.PROP_ARTIST)
				title = self.db.entry_get(entry, rhythmdb.PROP_TITLE)
				lrc_path = gen_lrc_path(self.prefs.get_pref('folder'), artist, title)
				self.lrc = load_lyrics(lrc_path, artist, title)
				if self.lrc != {}:
					self.osd_display('(%s - %s) prepared' % (artist, title))
			self.load_round += 1;
			try:
				self.osd_display(self.lrc[elapsed])
			except KeyError:
				pass
		return
		
	def playing_song_changed_handler(self, player, entry):
		logging.debug('enter')
		if entry:
			self.load_round = 0;
			# get playing song properties		
			artist = self.db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = self.db.entry_get(entry, rhythmdb.PROP_TITLE)
			logging.info('%s - %s' % (artist, title))
			lrc_path = gen_lrc_path(self.prefs.get_pref('folder'), artist, title)
			# load lyrics content
			self.lrc = load_lyrics(lrc_path, artist, title)
			if self.lrc == {}:
				if self.prefs.get_pref('download'):
					self.osd_display('(%s - %s) downloading' % (artist, title))
					Grabber(self.prefs.get_pref('engine'), artist, title, lrc_path[0], self.chooser).start()
				else:
					self.osd_display('(%s - %s) not found' % (artist, title))
			else:
				self.osd_display('(%s - %s) prepared' % (artist, title))
		logging.debug('leave')
		return

	def open_lyrics_popup(self, action):
		logging.debug('enter')
		source = self.shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			self.open_lyrics_file(entry)
		logging.debug('leave')
		return
	
	def open_lyrics_shortcut(self, action):
		logging.debug('enter')
		entry = self.player.get_playing_entry ()
		if entry:
			self.open_lyrics_file(entry)
		logging.debug('leave')
		return
	
	def open_lyrics_file(self, entry):
		logging.debug('enter')
		ret = False
		artist = self.db.entry_get(entry, rhythmdb.PROP_ARTIST)
		title = self.db.entry_get(entry, rhythmdb.PROP_TITLE)
		lrc_path = gen_lrc_path(self.prefs.get_pref('folder'), artist, title)
		for i in lrc_path:
			if os.path.exists(i):
				logging.info('open <%s>' % i)
				os.system('/usr/bin/xdg-open \"%s\"' % i)
				ret = True
				break
		if not ret:
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
		logging.basicConfig(level=logging.DEBUG, format= 'SogouLyrics %(levelname)-8s %(module)s::%(funcName)s - %(message)s')
		self.load_round = 0;
		self.prefs = Preference(self.find_file('prefs.glade'))
		self.chooser = LyricsChooser(self.find_file('lyrics-chooser.glade'))
		if not os.path.exists(self.prefs.get_pref('folder')):
			os.mkdir(self.prefs.get_pref('folder'))
		self.lrc = {}
		self.player = shell.get_player()
		self.shell = shell
		self.db = self.shell.get_property('db')
		self.handler = [
			self.player.connect('playing-song-changed', self.playing_song_changed_handler),
			self.player.connect('elapsed-changed', self.elapsed_changed_handler)]
		self.osd = eventbridge.OSD()
		#
		self.action = [
			gtk.Action('OpenLyricsPopup', _('Open Lyrics'), _('Open the lyrics of the selected song'), 'SogouLyrics'),
			gtk.Action('OpenLyricsShortcut', _('Open Playing _Lyrics'), _('Open the lyrics of the playing song'), 'SogouLyrics')]
		self.action[0].connect('activate', self.open_lyrics_popup)
		self.action[1].connect('activate', self.open_lyrics_shortcut)
		self.action_group = gtk.ActionGroup('SogouLyricsActions')
		self.action_group.add_action(self.action[0])
		self.action_group.add_action_with_accel (self.action[1], "<control>L")
		
		uim = shell.get_ui_manager ()
		uim.insert_action_group(self.action_group, 0)
		self.ui_id = uim.add_ui_from_file(self.find_file('ui.xml'))
		uim.ensure_update()
		#datefmt= '%m-%d %H:%M',)
		logging.info('Sogou Lyrics activated')
		return

	def deactivate(self, shell):
		for handler in self.handler:
			self.player.disconnect(handler)
		uim = shell.get_ui_manager()
		uim.remove_ui (self.ui_id)
		uim.remove_action_group (self.action_group)
		for action in self.action:
			del action
		#
		del self.prefs
		del self.chooser
		del self.shell
		del self.player
		del self.db
		del self.handler
		del self.lrc
		del self.osd
		del self.action_group
		del self.action
		logging.info('Sogou Lyrics deactivated')
		return

	def create_configure_dialog(self):
		dialog = self.prefs.get_dialog()
		dialog.present()
		return dialog
'''
if __name__ == '__main__':
	gtk.gdk.threads_init()
	gtk.gdk.threads_enter()
	gtk.main()
	gtk.gdk.threads_enter()
'''
