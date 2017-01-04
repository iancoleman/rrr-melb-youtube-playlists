# Depends on gdata - sudo pip install gdata
import gdata.youtube.service

import bs4
import datetime
import json
import os
import urllib
import urllib2



class AirnetParser():

	__use_the_internet = True
	__first_date = datetime.date(2011, 9, 17)
	__playlists = []

	def __init__(self):
		self.__build_program_list()
		self.__build_youtube_playlists()

	def __build_program_list(self):
		latest_date = self.__first_date
		today = datetime.date.today()
		while latest_date < today:
			program = Program(latest_date)
			self.__playlists.append(program)
			latest_date += datetime.timedelta(7)

	def __build_youtube_playlists(self):
		client = YoutubeClient()
		for program in self.__playlists:
			if not client.program_already_exists(program):
				playlist_uri = client.create_new_playlist(program.title, program.summary)
				if playlist_uri is not None:
					for song in program.songs:
						if song is not None and song.youtube_id is not None:
							client.add_song_to_playlist(song, program, playlist_uri)



class Program():

	#TODO make this work for all programs, not just beat orgy
	
	def __init__(self, date_of_program):
		self.date = date_of_program
		self.__scrape()

	def __scrape(self):
		date_str = self.date.isoformat()
		front_page_url = "http://airnet.org.au/program/javascriptEmbed.php?station=4&rpid=beat-orgy&view=3&helperStart=http%%3A%%2F%%2Fwww.rrr.org.au&time=%s" % date_str
		local_filename = "programs/beatorgy/%s.html" % date_str
		if (os.path.exists(local_filename)):
			all_songs_html = read_file(local_filename)
		else:
			all_songs_html = read_url(front_page_url)
			write_file(local_filename, all_songs_html)
		self.title = "RRR - Beat Orgy - %s" % date_str
		self.summary = self.__parse_summary(all_songs_html)
		self.songs = self.__parse_all_songs_html(all_songs_html)

	def __parse_all_songs_html(self, all_songs_html):
		songs = []
		if all_songs_html.find("Episode not found") > -1:
			return songs
		dom = bs4.BeautifulSoup(all_songs_html)
		tracks = dom.find("div", class_="trackList").table.contents
		for track in tracks:
			if type(track) == bs4.element.Tag:
				song_id = track.td.text
				song = Song(song_id)
				if song.is_valid:
					songs.append(song)
		return songs

	def __parse_summary(self, all_songs_html):
		return "102.7 FM Melbourne"

	def to_json(self):
		return {}




class Song():

	def __init__(self, airnet_id):
		if self.is_valid_song_id(airnet_id):
			self.airnet_id = airnet_id
			self.youtube_id = None
			self.__scrape()

	def is_valid_song_id(self, song_id):
		# TODO this can be improved with re, should be six digits long
		self.is_valid = len(song_id) > 5
		return self.is_valid

	def __scrape(self):
		song_url = "http://airnet.org.au/program/ajax-server/ajaxShowTrack.php?id=%s" % (self.airnet_id)
		local_filename = "beatorgy/%s.json" % self.airnet_id
		if os.path.exists(local_filename):
			song_json = read_file(local_filename)
		else:
			song_json = read_url(song_url) # Is sent with mimetype text/html ...boourns
			write_file(local_filename, song_json)
		self.__parse(song_json)

	def __parse(self, song_json):
		song_dict = json.loads(song_json)
		self.title = song_dict['title']
		self.artist = song_dict['artist']

		dom = bs4.BeautifulSoup(song_dict['text'])
		
		youtube = dom.find("embed")
		if type(youtube) == bs4.element.Tag:
			self.youtube = youtube["src"]
			self.youtube_id = self.youtube.split('/v/')[-1].split("&")[0]
		
		description = dom.find(class_="trackNotes-main")
		if type(description) == bs4.element.Tag:
			self.description = description.text.strip()
		else:
			self.description = None

		

class YoutubeClient():

	def __init__(self):
		self.__login()
		self.__existing_playlists = self.get_existing_playlists()

	def __login(self):
		credentials_string = read_file("credentials")
		credentials = json.loads(credentials_string)
		yt_service = gdata.youtube.service.YouTubeService()
		yt_service.email = credentials["email"]
		yt_service.password = credentials["password"]
		yt_service.source = credentials["source"]
		yt_service.developer_key = credentials["developer_key"]
		yt_service.client_id = credentials["client_id"]
		print "Authenticating with youtube"
		yt_service.ProgrammaticLogin()
		self.__yt_service = yt_service

	def get_existing_playlists(self):
		print "Fetching existing playlists from youtube"
		playlists = [] # Should be a set
		playlist_feed = self.__yt_service.GetYouTubePlaylistFeed(username='default')
		for entry in playlist_feed.entry:
			playlists.append({
				"title": entry.title.text,
				"summary": entry.content.text
				})
		return playlists

	def program_already_exists(self, program):
		for existing_playlist in self.__existing_playlists:
			title_matches = program.title == existing_playlist["title"]
			summary_matches = program.summary == existing_playlist["summary"]
			if title_matches and summary_matches:
				print "Playlist already exists on youtube - %s" % program.title
				return True
		return False

	def create_new_playlist(self, title, summary):
		print 'Adding new playlist - "%s" : "%s"' % (title, summary)
		try:
			new_public_playlistentry = self.__yt_service.AddPlaylist(title, summary)
			if isinstance(new_public_playlistentry, gdata.youtube.YouTubePlaylistEntry):
				print 'New playlist added  - "%s" : "%s"' % (title, summary)
				return "http://gdata.youtube.com/feeds/api/playlists/%s" % new_public_playlistentry.id.text.split('/')[-1]
		except:
			print "PLAYLIST NOT CREATED! %s" % (title)

	def add_song_to_playlist(self, song, program, playlist_uri):
		custom_video_title = "%s - %s" % (song.artist, song.title)
		custom_video_description = "%s - %s" % (program.title, program.summary)
		video_id = song.youtube_id
		playlist_uri = playlist_uri
		try:
			playlist_video_entry = self.__yt_service.AddPlaylistVideoEntryToPlaylist(playlist_uri, video_id, custom_video_title, custom_video_description)
			if isinstance(playlist_video_entry, gdata.youtube.YouTubePlaylistVideoEntry):
				print 'Video added: %s - %s' % (song.artist, song.title)
		except:
			print "Video NOT ADDED! %s - %s - %s" % (song.artist, song.title, song.youtube)



def read_url(url):
	print "Reading URL %s" % url[-40:]
	f = urllib.urlopen(url)
	content = f.read()
	return content

def read_file(filename):
	print "Reading file %s" % filename[-40:]
	f = open(filename)
	content = f.read()
	f.close()
	return content

def write_file(filename, content):
	f = open(filename, 'w')
	f.write(content)
	f.close()

AirnetParser()

