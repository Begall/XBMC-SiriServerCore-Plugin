from plugin import *
from editme import GetLogin 
from siriObjects.uiObjects import UIAddViews, UIListItem, UIDisambiguationList
from siriObjects.answerObjects import AnswerSnippet, AnswerObject, AnswerObjectLine
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

def hackygettitle(id, mtype):
    if mtype == 'movie':
       y = json.VideoLibrary.GetMovieDetails(movieid=id)
       x = y['moviedetails']['label']
    return x

def CreateListItem(id, mtype):
    item = UIListItem()
    if mtype == 'movie':
       y = json.VideoLibrary.GetMovieDetails(movieid=id, properties=['tagline', 'year', 'rating'])['moviedetails']
       m = [int(id), y['label'], y['year'], y['rating'], y['tagline']]
       item.selectionResponse = "%s (%s)\n\n'%s'" %(m[1], m[2], m[4])
    if mtype == 'album':
       y = json.AudioLibrary.GetAlbumDetails(albumid=id, properties=['title', 'description', 'artist', 'genre', 'year'])['albumdetails']
       m = [int(id), y['title'], y['artist'], y['year'], y['description']]
       item.selectionResponse = "%s (%s)\n\n'%s'" %(m[1], m[3], m[4])
    item.title = "%s (%s)" %(m[1], m[2])
    return item        

class XBMC2(Plugin):

      global json
      try:
         json = jsonrpclib.Server('%s/jsonrpc' %(get_url()))
      except IOError: 
         print "ERROR (XBMC Plugin): Incomplete XBMC login information, please edit ~/XBMC2/editme.py" 

      def CreateAnswerObject(self, id, mtype):
          if mtype == 'movie':
             y = json.VideoLibrary.GetMovieDetails(movieid=id, properties=['thumbnail', 'plot'])['moviedetails']
             m = ['http://%s:%s/vfs/%s' %(GetLogin()[0], GetLogin()[1], y['thumbnail']), y['label'], y['plot']]
             AnswerTitle, AnswerThumb, AnswerPlot = AnswerObject(title='Title',lines=[AnswerObjectLine(text=m[1])]), AnswerObject(title='Thumbnail',lines=[AnswerObjectLine(image=m[0])]), AnswerObject(title='Plot',lines=[AnswerObjectLine(text="'%s'" %(m[2]))])
             view1 = AnswerSnippet(answers=[AnswerTitle, AnswerThumb, AnswerPlot])
          if mtype == 'tvshow':
             y = json.VideoLibrary.GetEpisodeDetails(episodeid=id, properties=['thumbnail', 'plot', 'showtitle', 'season', 'episode'])['episodedetails']
             m = ['http://%s:%s/vfs/%s' %(GetLogin()[0], GetLogin()[1], y['thumbnail']), y['label'], y['plot'], y['showtitle'], y['season'], y['episode']]
             AnswerShowtitle, AnswerEpisode, AnswerThumb, AnswerPlot = AnswerObject(title='Show',lines=[AnswerObjectLine(text=m[3])]), AnswerObject(title='Episode',lines=[AnswerObjectLine(text="%ix%i. %s" %(m[4], m[5], m[1]))]), AnswerObject(title='Thumbnail',lines=[AnswerObjectLine(image="%s"%(m[0]))]), AnswerObject(title='Plot', lines=[AnswerObjectLine(text="'%s'" %(m[2]))])
             view1 = AnswerSnippet(answers=[AnswerShowtitle, AnswerEpisode, AnswerThumb, AnswerPlot])
          if mtype == 'album':
             y = json.AudioLibrary.GetAlbumDetails(albumid=id, properties=['thumbnail', 'year', 'artist', 'title', 'description'])['albumdetails']
             m = [y['thumbnail'], y['title'], y['artist'], y['year'], y['description']]
             AnswerTitle, AnswerThumb, AnswerInfo, AnswerArtist = AnswerObject(title='Album',lines=[AnswerObjectLine(text="%s (%s)" %(m[1], m[3]))]), AnswerObject(title='Art',lines=[AnswerObjectLine(image=m[0])]), AnswerObject(title='Description',lines=[AnswerObjectLine(text=m[4])]), AnswerObject(title='Artist', lines=[AnswerObjectLine(text=m[2])]) 
             view1 = AnswerSnippet(answers=[AnswerTitle, AnswerArtist, AnswerThumb, AnswerInfo])
          view = UIAddViews(self.refId)
          view.views = [view1]
          return view

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
             json.AudioLibrary.Clean()
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
 
      @register("en-US", ".*(pause|paws|place|holes|polls|kohls|kohl's|post|resume|porn) (?P<librarytype>[\w]+) player.*")
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
          lst = UIDisambiguationList()
          lst.items = []
          x = UIAddViews(self.refId)
          x.dialogPhase = x.DialogPhaseCompletionValue
          result = json.VideoLibrary.GetRecentlyAddedMovies(limits={'end': 10})
          for movie in result['movies']:
             lst.items.append(CreateListItem(movie['movieid'], 'movie'))
          x.views = [lst]
          self.say("", "Last 10 movies added...")
          self.sendRequestWithoutAnswer(x)
          self.complete_request()

      @register("en-US", "(?:Watch|Watchin|Watching) (?P<title>.*(?=season)|.*(?!season))(?:season (?P<season>[\d]+) episode (?P<episode>[\d]+))?")
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
                   z, found = self.CreateAnswerObject(tvshow['episodeid'], 'tvshow'), found + 1
                   self.say(self.sendRequestWithoutAnswer(z), "Now playing...") 
                   play(json,{'episodeid': tvshow['episodeid']}, 1)
                   break
             if found == 0:
                self.say("Couldn't find the episode you were looking for, sorry!")
             self.complete_request()
          else:
             foundinfo = []
             matches = ''
             result = json.VideoLibrary.GetMovies()
             for movie in result['movies']:
                 if stripped_title in ''.join(ch for ch in movie['label'] if ch.isalnum()).lower():
                    v, found = movie['movieid'], found + 1  
                    foundinfo.append(v)
             if found > 1:
                for x in foundinfo:
                   matches = matches + '%s. %s\n\n' %(x, hackygettitle(x, 'movie'))
                self.say("Found multiple matches...\n\n%s" %(matches), "")
                response = self.ask("", "Pick a number to play")
                try:
                   if int(response) in foundinfo:
                      z = self.CreateAnswerObject(int(response), 'movie')
                      self.say(self.sendRequestWithoutAnswer(z), "Now Playing...")
                      play(json,{'movieid': int(response)}, 1)
                   else:
                      self.say("That wasn't a choice, try again")
                except ValueError:
                   self.say("That wasn't a number silly!")
                   self.complete_request()
             elif found == 1:
                for x in foundinfo:
                   z = self.CreateAnswerObject(x, 'movie')
                   self.say(self.sendRequestWithoutAnswer(z), "Now playing...") 
                   play(json,{'movieid': x}, 1)
             elif found == 0:
                self.say("Couldn't find the movie you were looking for, sorry!")
             self.complete_request()
                      
      #Music Related Functions 

      @register("en-US", ".*list (?P<artistname>[^^]+) (album|albums)")
      def list_music(self, speech, langauge, matchedRegex):
          found, lst = 0, UIDisambiguationList()
          lst.items = []
          anchor = UIAddViews(self.refId)
          anchor.dialogPhase = anchor.DialogPhaseCompletionValue
          stripped_artistname = ''.join(ch for ch in matchedRegex.group('artistname') if ch.isalnum()).lower()
          if stripped_artistname == 'latest':
             result = json.AudioLibrary.GetRecentlyAddedAlbums(properties=['artist'], limits={'end': 10})
             for album in result['albums']:
                 lst.items.append(CreateListItem(album['albumid'], 'album'))
             anchor.views = [lst]
             self.say("", "Last 10 albums added...")
             self.sendRequestWithoutAnswer(anchor)
          else:
             result = json.AudioLibrary.GetAlbums(properties=['artist'])
             for album in result['albums']:
                if stripped_artistname in ''.join(ch for ch in album['artist'] if ch.isalnum()).lower():
                   lst.items.append(CreateListItem(album['albumid'], 'album'))
                   found = 1
             if found == 0:
                self.say("Sorry, I couldn't find the artist you're looking for")
             else:
                anchor.views = [lst]
                self.say("", "Albums for '%s'" %(string.capwords(matchedRegex.group('artistname'))))
                self.sendRequestWithoutAnswer(anchor)
          self.complete_request()
                     
      @register("en-US", ".*listen to (?P<musictype>[\w]+) (?P<title>[^^]+)")
      def play_music(self, speech, langauge, matchedRegex):
          found = 0
          musictype = matchedRegex.group('musictype')
          stripped_title = ''.join(ch for ch in matchedRegex.group('title') if ch.isalnum()).lower()
          if musictype == 'album' or 'albums':
             result = json.AudioLibrary.GetAlbums(properties=['artist'])
             for album in result['albums']:
                if stripped_title in ''.join(ch for ch in album['label'] if ch.isalnum()).lower():
                   z, found = self.CreateAnswerObject(album['albumid'], 'album'), 1
                   play(json, {'albumid': album['albumid']}, 0)
                   break
             if found == 0:
                self.say("Couldn't find the album you were looking for, sorry!")
             else:
                self.say(self.sendRequestWithoutAnswer(z), "Now playing...")
          else:
             self.say("Can only search for albums at the moment, sorry!")
          self.complete_request()
