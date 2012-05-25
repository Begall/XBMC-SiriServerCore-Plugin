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
         print "ERROR (XBMC Plugin): Incomplete XBMC login information, please edit ~/editme.py" 

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
             json.Player.PausePlay(playerid=1)
          elif librarytype == 'Music':
             json.Player.PausePlay(playerid=0)
          self.say(" ", "%s player paused/resumed" %(librarytype))
          self.complete_request()    

      #Video Related Functions

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
                   episodeid = tvshow['episodeid']
                   tvst = tvshow['showtitle']
                   tvsl = tvshow['label']
                   found = 1
                   self.say("Loading..." + '\n\n' "Show: '%s'" %(tvst) + '\n\n' + "Episode: '%s'" %(tvsl), " ")
                   play(json,{'episodeid': episodeid}, 1)
             if found == 0: 
                self.say("Couldn't find the episode you were looking for, sorry!")     
             self.complete_request()
          else: 
             result = json.VideoLibrary.GetMovies()
             for movie in result['movies']:
                if stripped_title in ''.join(ch for ch in movie['label'] if ch.isalnum()).lower():
                   movieid = movie['movieid']
                   mn = movie['label']
                   found = 1 
                   self.say("Loading..." + '\n\n Title :  ' + '%s' %(mn), "")
                   play(json,{'movieid': movieid}, 1)
                   break 
             if found == 0:
                self.say("Couldn't find the movie you were looking for, sorry!") 
             self.complete_request()      
                      
