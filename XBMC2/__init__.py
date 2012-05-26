from plugin import *
from editme import GetLogin 
import string

try:
    import jsonrpclib 
except ImportError:
    raise NecessaryModuleNotFound('XBMC plugin will not work: JSONRPCLIB not installed. To install, run "easy_install jsonrpclib"')

def get_url():
    if GetLogin()[0] and GetLogin()[1] and GetLogin()[2] and GetLogin()[3] != None: 
       return 'http://%s:%s@%s:%s' %(GetLogin()[2], GetLogin()[3], GetLogin()[0], GetLogin()[1]) 
    else: 
       return '' 

def play(json, item, playerid):
    json.Playlist.Clear(playlistid=playerid)
    json.Playlist.Add(playlistid=playerid, item=item)
    json.Player.Open({ 'playlistid' : playerid})

class XBMC2(Plugin):

      global json
      try:
         json = jsonrpclib.Server('%s/jsonrpc' %(get_url()))
      except IOError: 
         print "ERROR (XBMC Plugin): Incomplete XBMC login information, please edit ~/XBMC2/editme.py" 

      # Utility Functions

      @register("en-US", "xbmc help") 
      def help(self, speech, langauge, matchedRegex):
          self.say("Placeholder", "Here is a list of available commands...") 
          self.complete_request()

      @register("en-US", ".*update (?P<librarytype>[\w]+) library.*")
      def update_command(self, speech, langauge,  matchedRegex):
         librarytype = string.capwords(matchedRegex.group('librarytype'))
         if librarytype == 'Video':
            json.VideoLibrary.Scan()
         elif librarytype == 'Music':
            json.AudioLibrary.Scan()
         self.say("%s library updated" %(librarytype))
         self.complete_request()
      
      @register("en-US", ".*clean (?P<librarytype>[\w]+) library.*")
      def clean_command(self, speech, langauge, matchedRegex):
          librarytype = string.capwords(matchedRegex.group('librarytype'))
          if librarytype == 'Video':
             json.VideoLibrary.Clean()
          elif librarytype == 'Music':
             json.AudioLibray.Scan()
          self.say("%s library cleaned" %(librarytype)) 
          self.complete_request()

      # Player Controls
             
      @register("en-US", ".*stop (?P<librarytype>[\w]+) player.*")
      def stop_command(self, speech, langauge, matchedRegex):
          librarytype = string.capwords(matchedRegex.group('librarytype'))
          if librarytype == 'Video': 
             json.Player.Stop(playerid=1)
          elif librarytype == 'Music':
             json.Player.Stop(playerid=0)
          self.say("%s player stopped" %(librarytype))
          self.complete_request()  
 
      @register("en-US", ".*(pause|paws|place|holes|polls|kohls|kohl's|post|resume) (?P<librarytype>[\w]+) player.*")
      def pause_command(self, speech, langauge, matchedRegex):
          librarytype = string.capwords(matchedRegex.group('librarytype'))
          if librarytype == 'Video': 
             json.Player.PlayPause(playerid=1)
          elif librarytype == 'Music':
             json.Player.PlayPause(playerid=0)
          self.say("%s player paused/resumed" %(librarytype), "")
          self.complete_request()    

      #Video Related Functions

      @register("en-US", ".*list latest (movies|movie)")
      def listlatestmovies(self, speech, langauge):
          matches = ''
          result = json.VideoLibrary.GetRecentlyAddedMovies()
          for i, movie in enumerate(result['movies']):
             matches = matches + "%i. %s\n\n" %(i, movie['label'])
          self.say("Latest added movies...\n\n%s" %(matches), "")
          self.complete_request()

      @register("en-US", u"(?:Watch|Put On) (?P<title>.*(?=season)|.*(?!season))(?:season (?P<season>[\d]+) episode (?P<episode>[\d]+))?")
      def mainvideo_command(self, speech, langauge, matchedRegex):
          found = 0
          stripped_title = ''.join(ch for ch in matchedRegex.group('title') if ch.isalnum()).lower()
          if matchedRegex.group('season') != None:
             result = json.VideoLibrary.GetEpisodes(properties = ['showtitle'])
             if len(matchedRegex.group('episode')) > 1: 
                EpNo = matchedRegex.group('season') + 'x' + matchedRegex.group('episode')
             else: 
                EpNo = matchedRegex.group('season') + 'x' + '0' + matchedRegex.group('episode')
             for tvshow in result['episodes']:
                if stripped_title in ''.join(ch for ch in tvshow['showtitle'] if ch.isalnum()).lower() and EpNo in tvshow['label']:
                   episodeid, tvst, tvsl, found = tvshow['episodeid'], tvshow['showtitle'], tvshow['label'], 1
                   self.say("Loading..." + '\n\n' "Show: '%s'" %(tvst) + '\n\n' + "Episode: '%s'" %(tvsl), " ")
                   play(json,{'episodeid': episodeid}, 1)
                   break
             if found == 0: 
                self.say("Couldn't find the episode you were looking for, sorry!")     
             self.complete_request()
          else: 
             result = json.VideoLibrary.GetMovies()
             for movie in result['movies']:
                if stripped_title in ''.join(ch for ch in movie['label'] if ch.isalnum()).lower():
                   movieid, mn, found = movie['movieid'], movie['label'], 1
                   self.say("Loading..." + '\n\n Title :  ' + '%s' %(mn), "")
                   play(json,{'movieid': movieid}, 1)
                   break 
             if found == 0:
                self.say("Couldn't find the movie you were looking for, sorry!") 
             self.complete_request()      
                      
      #Music Related Functions 

      @register("en-US", ".*list (?P<artistname>[^^]+) (album|albums)")
      def list_music(self, speech, langauge, matchedRegex):
          found = 0
          albumList = ''
          stripped_artistname = ''.join(ch for ch in matchedRegex.group('artistname') if ch.isalnum()).lower()
          if stripped_artistname == 'latest': 
             result = json.AudioLibrary.GetRecentlyAddedAlbums(properties=['artist'])
             matchedArtist = 'Latest Added' 
             for index, album in enumerate(result['albums']):
                albumList = albumList + '%s. %s' %(index, album['label']) + '\n' + '  - %s' %(album['artist']) + '\n\n'
                found = 1
          else:
             result = json.AudioLibrary.GetAlbums(properties=['artist'])
             for index, album in enumerate(result['albums']):
                if stripped_artistname in ''.join(ch for ch in album['artist'] if ch.isalnum()).lower():
                   albumList, matchedArtist, found = albumList + '%s. %s' %(index, album['label']) + '\n\n', album['artist'], 1
          if found == 0: 
             self.say("Sorry, I couldn't find the artist you're looking for")
          else:
             self.say("Albums for '%s' :" %(matchedArtist) + '\n\n' + '%s' %(albumList), "Here you go...")
          self.complete_request()
                     
      @register("en-US", ".*listen to (?P<musictype>[\w]+) (?P<title>[^^]+)")
      def play_music(self, speech, langauge, matchedRegex):
          found = 0
          musictype = matchedRegex.group('musictype')
          stripped_title = ''.join(ch for ch in matchedRegex.group('title') if ch.isalnum()).lower()
          if musictype == 'album' or 'albums':
             result = json.AudioLibrary.GetAlbums(properties=['artist'])
             for index, album in enumerate(result['albums']):
                if stripped_title in ''.join(ch for ch in album['label'] if ch.isalnum()).lower():
                   albumid, name, artist, found  = album['albumid'], album['label'], album['artist'], 1
                   break 
             if found == 0:
                self.say("Couldn't find the album you were looking for, sorry!") 
             else: 
                play(json, {'albumid': albumid}, 0)
                self.say('Now Playing... \n\n Title: %s' %(name) + '\n' + '        By: %s' %(artist), "")
          else: 
             self.say("Can only search for albums at the moment, sorry!") 
          self.complete_request()
