import os, sys, ClientCookie, urllib2, re
import rhythmdb, rb
from gnomeosd import eventbridge
import gobject, gtk
from ConfigureDialog import ConfigureDialog
import gconf

# global settings
LRCDIR = os.path.expanduser('~/.lyrics')
TOKEN_STRIP = ['\([^\)]*\)', ' ']
SHADOW = 'off'
TRANSLUCENT = 'off'
TIMEOUT = 20000
SIZE = 20000
MESSAGE_TEMPLATE = "<message id='SogouLyrics' animations='%%s' osd_fake_translucent_bg='%s' drop_shadow='%s' osd_vposition='%%s' osd_halignment='%%s'  hide_timeout='%d'><span size='%d' foreground='%%s'>%%s</span></message>" % (TRANSLUCENT, SHADOW, TIMEOUT, SIZE)

ui_str = """
<ui>
  <popup name="BrowserSourceViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenLyricsPopup" action="OpenLyrics"/>
    </placeholder>
  </popup>

  <popup name="PlaylistViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenLyricsPopup" action="OpenLyrics"/>
    </placeholder>
  </popup>

  <popup name="QueuePlaylistViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenLyricsPopup" action="OpenLyrics"/>
    </placeholder>
  </popup>

  <popup name="PodcastViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenLyricsPopup" action="OpenLyrics"/>
    </placeholder>
  </popup>
</ui>
"""

def detect_charset(s):
	charsets = ('iso-8859-1', 'gbk', 'utf-8')
	for charset in charsets:
		try:
			return unicode(unicode(s, 'utf-8').encode(charset), 'gbk')
		except:
			continue
	return s

def parse_lyrics(lines):
	content = {}
	re_ti = re.compile('\[ti:[^\]]*\]')
	re_ar = re.compile('\[ar:[^\]]*\]')
	re_offset = re.compile('\[offset:[^\]]*\]')
	re_lrc = re.compile('(\[[0-9\.:]*\])+.*')
	re_time = re.compile('\[[0-9]{2}:[0-9]{2}\.[0-9]{2}\]')
	offset = 0
	for line in lines:
		# search for title property
		m = re_ti.search(line)
		if not m is None:
			segment = m.group(0)
			content['ti'] = segment[4:-1]
		# search for artist property
		m = re_ar.search(line)
		if not m is None:
			segment = m.group(0)
			content['ar'] = segment[4:-1]
		# search for offset property
		m = re_offset.search(line)
		if not m is None:
			segment = m.group(0)
			offset = int(segment[8:-1])
			content['offset'] = offset
		# parse lrc
		m = re_lrc.match(line)
		if not m is None:
			pos = 0
			tm = re_time.findall(line)
			for time in tm:
				pos = pos + len(time)
			lrc = m.group(0)[pos:]
			for time in tm:
				try:
					minute = int(time[1:3])
					second = int(time[4:6])
					centi = int(time[7:9])
					key = int(round(((minute * 60 + second) * 1000 + centi * 10 + offset) / 1000.0))
					content[key] = lrc
				except ValueError:
					print 'invalid timestamp %s' % time
	return content

def clean_token(token):
	result = token.lower()
	for strip in TOKEN_STRIP:
		result = re.sub(strip, '', result)
	return result
	
def verify_lyrics(content, artist, title):
	retval = 0
	if not content.has_key('ar'):
		print 'cannot find artist in lyrics'
	elif not content.has_key('ti'):
		print 'cannot find title in lyrics'
	else:
		ar = content['ar']
		ti = content['ti']
		print '%s - %s' % (ar, ti)
		ar = ar.lower().replace(' ', '')
		ti = ti.lower().replace(' ', '')
		ar1 = clean_token(artist)
		ti1 = clean_token(title)
		if ar.find(ar1) != -1 and ti.find(ti1) != -1:
			retval = 1
	return retval
			
def download_lyrics(artist, title):
	retval = {}
	# grab song search page
	title_encode = urllib2.quote(detect_charset(clean_token(title)).encode('gbk'))
	artist_encode = urllib2.quote(detect_charset(clean_token(artist)).encode('gbk'))
	uri = 'http://mp3.sogou.com/music.so?query=%s%%20%s' % (artist_encode, title_encode)
	print 'search page <%s>' % uri
	cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
	for line in cache:
		# grab lyrics search page, only use the first
		m = re.search('geci\.so\?[^\"]*', line.decode('gbk'))
		if not m is None:
			uri = 'http://mp3.sogou.com/%s' % m.group(0)
			print 'lyrics page <%s>' % uri
			cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
			for line in cache:
				# grab lyrics file uri, try all of them
				m = re.search('downlrc\.jsp\?[^\"]*', line.decode('gbk'))
				if not m is None:				
					uri = 'http://mp3.sogou.com/%s' % m.group(0)
					print 'lyrics file <%s>' % uri
					cache = ClientCookie.urlopen(ClientCookie.Request(uri)).readlines()
					lrc = []
					for line in cache:
						lrc.append(line.decode('gbk').encode('utf-8'))
					lrc_content = parse_lyrics(lrc)
					if verify_lyrics(lrc_content, artist, title):
						lrc_path = '%s/%s - %s.lrc' % (LRCDIR, artist, title)
						open(lrc_path, 'w').writelines(lrc)
						retval = lrc_content
						break
			break
	return retval

class SogouLyrics(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)

	def osd_display(self, message):
		if self.config.get_config('display'):
			code = MESSAGE_TEMPLATE % (self.config.get_config('animation'), self.config.get_config('vpos'), self.config.get_config('halign'), self.config.get_config('fgcolor'), message)
			self.osd.send(code)
		
	def elapsed_changed_handler(self, player, playing):
		if playing:
			elapsed = player.get_playing_time()
			try:
				self.osd_display(self.lrc[elapsed])
			except KeyError:
				pass
		return

	def playing_song_changed_handler(self, player, entry):
		print 'enter'
		if entry:
			# get playing song properties		
			db = self.shell.get_property ('db')
			artist = db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = db.entry_get(entry, rhythmdb.PROP_TITLE)
			print '%s - %s' % (artist, title)
			lrc_path = '%s/%s - %s.lrc' % (LRCDIR, artist, title)
			# load lyrics content
			self.lrc = {}
			if os.path.exists(lrc_path) and os.path.isfile(lrc_path):
				self.lrc = parse_lyrics(open(lrc_path, 'r').readlines())
				if not verify_lyrics(self.lrc, artist, title):
					self.lrc = {}
					print 'broken lyrics file %s moved to %s.bak' % (lrc_path, lrc_path)
					try:
						os.rename(lrc_path, '%s.bak' % lrc_path)
					except OSError:
						print 'move broken lyrics file failed'
			if self.lrc == {} and self.config.get_config('download'):
				self.lrc = download_lyrics(artist, title)
			if self.lrc == {}:
				self.osd_display('(%s - %s) not found' % (artist, title))
			else:
				self.osd_display('(%s - %s) prepared' % (artist, title))
		print 'leave'
		return

	def playing_changed_handler(self, player, playing):
		# set player status		
		self.playing = playing
		print 'player status changed to %d' % playing
		return

	def open_lyrics(self, action, shell):
		print 'enter'
		source = shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			entry = selected[0]
			db = self.shell.get_property ('db')
			artist = db.entry_get(entry, rhythmdb.PROP_ARTIST)
			title = db.entry_get(entry, rhythmdb.PROP_TITLE)
			lrc_path = '%s/%s - %s.lrc' % (LRCDIR, artist, title)
			if os.path.exists(lrc_path):
				print 'open lyrics at <%s>' % lrc_path
				os.system('/usr/bin/xdg-open \"%s\"' % lrc_path)
			else:
				print 'lyrics not found (%s - %s)' % (artist, title)
				message = 'Artist:\t%s\nTitle:\t%s\nLyrics not found!' % (artist, title)
				dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=message)
				dlg.set_title('Open Lyrics')
				dlg.run()
				dlg.destroy()
		print 'leave'
		return
				
	def activate(self, shell):
		if not os.path.exists(LRCDIR):
			os.mkdir(LRCDIR)
		self.playing = 0
		self.lrc = {}
		self.player = shell.get_player()
		self.shell = shell
		self.handler = [
			self.player.connect('playing-song-changed', self.playing_song_changed_handler),
			self.player.connect('elapsed-changed', self.elapsed_changed_handler),
			self.player.connect('playing-changed', self.playing_changed_handler)]
		self.osd = eventbridge.OSD()
		#
		self.action = gtk.Action('OpenLyrics', _('Open lyrics'),
					 _('Open the lyrics of the selected song'),
					 'SogouLyrics')
		self.activate_id = self.action.connect('activate', self.open_lyrics, shell)
		
		self.action_group = gtk.ActionGroup('OpenLyricsPluginActions')
		self.action_group.add_action(self.action)
		
		uim = shell.get_ui_manager ()
		uim.insert_action_group(self.action_group, 0)
		self.ui_id = uim.add_ui_from_string(ui_str)
		uim.ensure_update()
		self.config = ConfigureDialog(self.find_file("ConfigureDialog.glade"))
		print 'Sogou Lyrics activated'
		return

	def deactivate(self, shell):
		del self.config
		for handler in self.handler:
			self.player.disconnect(handler)
		del self.shell
		del self.player
		del self.lrc
		del self.osd
		#
		uim = shell.get_ui_manager()
		uim.remove_ui (self.ui_id)
		uim.remove_action_group (self.action_group)

		self.action_group = None
		self.action = None
		print 'Sogou Lyrics deactivated'
		return

	def create_configure_dialog(self):
		dialog = self.config.get_dialog()
		dialog.present()
		return dialog
