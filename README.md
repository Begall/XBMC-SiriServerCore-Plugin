XBMC-SiriServerCore-Plugin
==========================

Revised plugin for SiriServerCore that lets you control XBMC with your voice. 

Original code can be found here: 

https://github.com/Eichhoernchen/SiriServer/blob/master/plugins/XBMC.py

Full credit to Gustavo Hoirisch/Pieter Janssens, original creators



Install Instructions:

1. Open terminal and type 'easy_install jsonrpclib' 

2. Unpack and copy the XBMC2 folder into your 'plugins/' folder in the SiriServerCore install

3. Open plugins.conf in the main SiriServerCore directory and add 'XBMC2' in a new line at the bottom of the list

4. Open editme.py in the plugins/XBMC2 folder and add the host/port/username/password of your XBMC installation



What you can do with this plugin:

- Update/Clean your libraries ('Update/Clean music/video library') 

- Stop the audio/video players ('Stop music/video player') 

- Pause/Resume the audio/video players ('Pause/Resume music/video player') 

- List the latest added movies 'List latest movies'

- Play a specified TV Show episode 'Watch (SHOWTITLE) Season (#) Episode (#)' 
 
- Play a specified movie 'Watch (MOVIETITLE)' 
  - If multiple matches are found, you will be presented with a choice and asked to pick a number

- List the latest/specified artist albums 'List (ARTISTNAME/Latest) albums'

- Play a specified album 'Listen to album (ALBUMTITLE)' 



Future features to be implemented: 

- Playing latest added TV Show episodes

- Playing random TV Show episodes

- Letting users pick which to play from list when multiple albums are found

- Displaying fanart with responses


Let me know what you think!
