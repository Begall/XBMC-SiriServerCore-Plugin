from plugin import *
from editme import GetLogin 
from siriObjects.uiObjects import UIAddViews, UIListItem, UIDisambiguationList
from siriObjects.answerObjects import AnswerSnippet, AnswerObject, AnswerObjectLine
import string, random, urllib

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

def GetMovieTitle(id):
    return json.VideoLibrary.GetMovieDetails(movieid=id)['moviedetails']['label']

def StrippedForSearch(value):
    return ''.join(ch for ch in value if ch.isalnum()).lower()

def CreateListItem(id, mtype):
    item = UIListItem()
    
    if mtype == 'movie':
       y = json.VideoLibrary.GetMovieDetails(movieid=id, properties=['year', 'rating', 'plot'])['moviedetails']
       m = [int(id), y['label'], y['year'], y['rating'], y['plot']]
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
      
      def CreateUIView(self): 
          dialog = UIAddViews(self.refId)
          dialog.dialogPhase = dialog.DialogPhaseCompletionValue
          return dialog
      
      def CreateEmptyList(self): 
          list = UIDisambiguationList()
          list.items = [] 
          return list 
       
      def SendAnswer(self, answerdata, answertype, requesttype, requesttext=""):
          object = self.CreateAnswerObject(answerdata, answertype)
          
          if requesttype == 'NoAnswer': 
             return self.say(self.sendRequestWithoutAnswer(object), requesttext)
      
      
      def CreateAnswerObject(self, id, mtype):
      
          if mtype == 'movie':
             y = json.VideoLibrary.GetMovieDetails(movieid=id, properties=['thumbnail', 'plot'])['moviedetails']
             print 'http://%s:%s/vfs/%s' %(GetLogin()[0], GetLogin()[1], urllib.urlencode({'': y['thumbnail']})[1:])
             m = ['http://%s:%s/vfs/%s' %(GetLogin()[0], GetLogin()[1], urllib.urlencode({'': y['thumbnail']})[1:]), y['label'], y['plot']]
             AnswerTitle, AnswerThumb, AnswerPlot = AnswerObject(title='Title',lines=[AnswerObjectLine(text=m[1])]), AnswerObject(title='Thumbnail',lines=[AnswerObjectLine(image=m[0])]), AnswerObject(title='Plot',lines=[AnswerObjectLine(text="'%s'" %(m[2]))])
             view1 = AnswerSnippet(answers=[AnswerTitle, AnswerThumb, AnswerPlot])
             
          if mtype == 'tvshow':
             y = json.VideoLibrary.GetEpisodeDetails(episodeid=id, properties=['thumbnail', 'plot', 'showtitle', 'season', 'episode'])['episodedetails']
             m = ['http://%s:%s/vfs/%s' %(GetLogin()[0], GetLogin()[1], urllib.urlencode({'': y['thumbnail']})[1:]), y['label'], y['plot'], y['showtitle'], y['season'], y['episode']]
             AnswerShowtitle, AnswerEpisode, AnswerThumb, AnswerPlot = AnswerObject(title='Show',lines=[AnswerObjectLine(text=m[3])]), AnswerObject(title='Episode',lines=[AnswerObjectLine(text="%ix%i. %s" %(m[4], m[5], m[1]))]), AnswerObject(title='Thumbnail',lines=[AnswerObjectLine(image="%s"%(m[0]))]), AnswerObject(title='Plot', lines=[AnswerObjectLine(text="'%s'" %(m[2]))])
             view1 = AnswerSnippet(answers=[AnswerShowtitle, AnswerEpisode, AnswerThumb, AnswerPlot])
             
          if mtype == 'album':
             y = json.AudioLibrary.GetAlbumDetails(albumid=id, properties=['thumbnail', 'year', 'artist', 'title', 'description'])['albumdetails']
             m = ['http://%s:%s/vfs/%s' %(GetLogin()[0], GetLogin()[1], urllib.urlencode({'': y['thumbnail']})[1:]), y['title'], y['artist'], y['year'], y['description']]
             print m[0] 
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
            self.say("%s library update in progress..." %(librarytype))
            
         elif librarytype == 'Music' or librarytype == 'Audio':
            json.AudioLibrary.Scan()
            self.say("%s library update in progress..." %(librarytype))
            
         else:
            self.say("Player not recognised, sorry!") 
            
         self.complete_request()
      
      @register("en-US", ".*clean (?P<librarytype>[\w]+) library.*")
      def clean_command(self, speech, langauge, matchedRegex):
          librarytype = string.capwords(matchedRegex.group('librarytype'))
          
          if librarytype == 'Video':
             json.VideoLibrary.Clean()
             self.say("%s library clean in progress..." %(librarytype))
             
          elif librarytype == 'Music' or librarytype == 'Audio':
             json.AudioLibrary.Clean()
             self.say("%s library clean in progress..." %(librarytype)) 
             
          else: 
             self.say("Player not recognised, sorry!") 
             
          self.complete_request()

          
      # Player Controls
             
      @register("en-US", ".*stop (?P<librarytype>[\w]+) player.*")
      def stop_command(self, speech, langauge, matchedRegex):
          librarytype = string.capwords(matchedRegex.group('librarytype'))
          
          if librarytype == 'Video': 
             json.Player.Stop(playerid=1)
             self.say("%s player stopped" %(librarytype))
             
          elif librarytype == 'Music' or librarytype == 'Audio':
             json.Player.Stop(playerid=0)
             self.say("%s player stopped" %(librarytype))
             
          else:
             self.say("Player not recognised, sorry!") 
             
          self.complete_request()  
 
      @register("en-US", ".*(pause|paws|place|holes|polls|kohls|kohl's|post|resume|porn) (?P<librarytype>[\w]+) player.*")
      def pause_command(self, speech, langauge, matchedRegex):
          librarytype = string.capwords(matchedRegex.group('librarytype'))
          
          if librarytype == 'Video': 
             json.Player.PlayPause(playerid=1)
             self.say("%s player paused/resumed" %(librarytype), "")
             
          elif librarytype == 'Music' or librarytype == 'Audio':
             json.Player.PlayPause(playerid=0)
             self.say("%s player paused/resumed" %(librarytype), "")
             
          else:
             self.say("Player not recognised, sorry!") 
             
          self.complete_request()    

          
      #Video Related Functions

      @register("en-US", ".*list latest (movies|movie)")
      def listlatestmovies(self, speech, langauge):
          lst = self.CreateEmptyList() 
          view = self.CreateUIView()
          result = json.VideoLibrary.GetRecentlyAddedMovies(limits={'end': 10})
          
          for movie in result['movies']:
             lst.items.append(CreateListItem(movie['movieid'], 'movie'))
             
          view.views = [lst]
          self.say(self.sendRequestWithoutAnswer(view), "Last 10 movies added...")
          self.complete_request()

      @register("en-US", "(?:Watch|Watchin|Watching) (?P<title>.*(?=season)|.*(?!season))(?:season (?P<season>[\d]+) episode (?P<episode>[\d]+))?")
      def mainvideo_command(self, speech, langauge, matchedRegex):
          found = 0
          title = matchedRegex.group('title')

          if matchedRegex.group('season') != None:
             result = json.VideoLibrary.GetEpisodes(properties = ['showtitle'])
             
             if len(matchedRegex.group('episode')) > 1:
                EpNo = matchedRegex.group('season') + 'x' + matchedRegex.group('episode')
             
             else:
                EpNo = matchedRegex.group('season') + 'x' + '0' + matchedRegex.group('episode')
             
             for tvshow in result['episodes']:
                
                if StrippedForSearch(title) in StrippedForSearch(tvshow['showtitle']) and EpNo in tvshow['label']:
                   found = 1
                   self.SendAnswer(tvshow['episodeid'], 'tvshow', 'NoAnswer', "Now playing...") 
                   play(json,{'episodeid': tvshow['episodeid']}, 1)
                   break
             
             if found == 0:
                self.say("Couldn't find the episode you were looking for, sorry!")

          else: 
             foundinfo = []
             
             if len(title.split()) > 1: 
                firstword, rest = title.split(' ', 1)
             
             else:
                firstword, rest = title 
             
             
             if firstword == 'random' or firstword == 'randoms':
                result = json.VideoLibrary.GetEpisodes(properties = ['showtitle'])
                
                for tvshow in result['episodes']:
                   
                   if StrippedForSearch(rest) in StrippedForSearch(tvshow['showtitle']):
                      foundinfo.append(tvshow['episodeid'])
                      found = 1
                
                if found == 1:
                   pickone = random.choice(foundinfo)
                   self.SendAnswer(pickone, 'tvshow', 'NoAnswer', "Now playing...") 
                   play(json,{'episodeid': pickone}, 1)
                
                else:
                   self.say("Couldn't find that show, sorry!")


             elif firstword == 'latest': 
                result = json.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['showtitle', 'playcount'])
                
                for tvshow in result['episodes']: 
                
                   if StrippedForSearch(rest) in StrippedForSearch(tvshow['showtitle']) and tvshow['playcount'] == 0:
                      found = 1
                      episode = tvshow['episodeid']
                      break
                      
                if found == 1: 
                   self.SendAnswer(episode, 'tvshow', 'NoAnswer', "Now playing...") 
                   play(json,{'episodeid': episode}, 1) 
                
                else: 
                   self.say("No unwatched recent episodes, sorry!")

 
             else:
                matches = ''
                result = json.VideoLibrary.GetMovies()
                
                for movie in result['movies']:
                
                    if StrippedForSearch(title) in StrippedForSearch(movie['label']):
                       v = movie['movieid']
                       found += 1 
                       foundinfo.append(v)
                       
                if found > 1:               
                   
                   for i, movieid in enumerate(foundinfo):                
                   
                      matches = matches + '%s. %s\n\n' %(i+1, GetMovieTitle(movieid)) # Don't start at 0 
                      
                   self.say("Found multiple matches...\n\n%s" %(matches), "")
                   response = self.ask("", "Pick a number to play")
                         
                   try:
                      selection = foundinfo[int(response)-1]   # Go back to 0 starting index 
                
                   except IndexError:
                      self.say("That wasn't a choice, try again") # When index does not exist 
                      self.complete_request()                    
 
                   except NameError, ValueError: 
                      self.say("That wasn't a number silly!")
                      self.complete_request()                    
                
                   self.SendAnswer(selection, 'movie', 'NoAnswer', "Now playing...") 
                   play(json,{'movieid': selection}, 1)

                elif found == 1:                
                   self.SendAnswer(foundinfo[0], 'movie', 'NoAnswer', "Now playing...")
                   play(json,{'movieid': foundinfo[0]}, 1)
                      
                elif found == 0:               
                   self.say("Couldn't find the movie you were looking for, sorry!")
                   
          self.complete_request()

          
      #Music Related Functions 
      
      @register("en-US", ".*list (?P<artistname>[^^]+) (album|albums)")
      def list_music(self, speech, langauge, matchedRegex):
          found = 0
          lst = self.CreateEmptyList() 
          view = self.CreateUIView()
          lst.items = []
          stripped_artistname = StrippedForSearch(matchedRegex.group('artistname'))
          
          if stripped_artistname == 'latest':
             result = json.AudioLibrary.GetRecentlyAddedAlbums(properties=['artist'], limits={'end': 10})
             
             for album in result['albums']:
                lst.items.append(CreateListItem(album['albumid'], 'album'))
                 
             view.views = [lst]
             self.say("", "Last 10 albums added...")
             self.sendRequestWithoutAnswer(view)
             
          else:         
             result = json.AudioLibrary.GetAlbums(properties=['artist'])
            
             for album in result['albums']:
             
                if stripped_artistname in StrippedForSearch(album['artist']):
                   lst.items.append(CreateListItem(album['albumid'], 'album'))
                   found = 1
                   
             if found == 0:           
                self.say("Sorry, I couldn't find the artist you're looking for")
                
             else:            
                view.views = [lst]
                self.say("", "Albums for '%s'" %(string.capwords(matchedRegex.group('artistname'))))
                self.sendRequestWithoutAnswer(view)
          
          self.complete_request()
                     
                     
      @register("en-US", ".*listen to (?P<musictype>[\w]+) (?P<title>[^^]+)")
      def play_music(self, speech, langauge, matchedRegex):
          found = 0
          musictype = matchedRegex.group('musictype')
          
          if musictype == 'album' or muisctype == 'albums':
             result = json.AudioLibrary.GetAlbums(properties=['artist'])
             
             for album in result['albums']:
             
                if StrippedForSearch(matchedRegex.group('title')) in StrippedForSearch(album['label']):
                   found = 1
                   self.SendAnswer(album['albumid'], 'album', 'NoAnswer', "Now playing...")                   
                   play(json, {'albumid': album['albumid']}, 0)
                   break
                   
             if found == 0:
                self.say("Couldn't find the album you were looking for, sorry!")
                
          elif musictype == 'song' or musictype == 'track': 
#             result = json.AudioLibrary.GetSongs(properties=['artist'])
#             for song in result['songs']: 
             self.say("Can only search for albums at the moment, sorry!")
             
          else: 
             self.say("Can only search for albums at the moment, sorry!") 
             
          self.complete_request()
