#from plugin import *
from editme import GetLogin 

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

class XBMC2():

      global json
      try:
         json = jsonrpclib.Server('%s/jsonrpc' %(get_url()))
      except IOError: 
         print "ERROR: Incomplete XBMC login information, please edit ~/editme.py" 


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
 
      @register("en-US", ".*(pause|paws|place|holes|polls|kohls|kohl's|post|resume) (?P<librarytype>[\w]+ player.*")
      def pause_command(self, speech, langauge, matchedRegex):
          librarytype = string.capwords(matchedRegex.group('librarype'))
          if librarytype == 'Video': 
             json.Player.PausePlay(playerid=1)
          elif librarytype == 'Music':
             json.Player.PausePlay(playerid=0)
          self.say(" ", "%s player paused/resumed" %(librarytype))
          self.complete_request()    


