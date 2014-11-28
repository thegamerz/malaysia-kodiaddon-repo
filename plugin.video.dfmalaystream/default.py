import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string, sys, os
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from htmlentitydefs import name2codepoint as n2cp
import HTMLParser

try:
	from sqlite3 import dbapi2 as sqlite
	print "Loading sqlite3 as DB engine"
except:
	from pysqlite2 import dbapi2 as sqlite
	print "Loading pysqlite2 as DB engine"

addon_id = 'plugin.video.dfmalaystream'
plugin = xbmcaddon.Addon(id=addon_id)
#DB = os.path.join(xbmc.translatePath("special://database"), 'dfv.db')
BASE_URL = 'http://malaystream.zapto.org'
net = Net()
addon = Addon('plugin.video.dfmalaystream', sys.argv)

###### PATHS ###########
AddonPath = addon.get_path()
IconPath = AddonPath + "/icons/"
FanartPath = AddonPath + "/icons/"

##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
content = addon.queries.get('content', None)
query = addon.queries.get('query', None)
startPage = addon.queries.get('startPage', None)
numOfPages = addon.queries.get('numOfPages', None)
listitem = addon.queries.get('listitem', None)
urlList = addon.queries.get('urlList', None)
section = addon.queries.get('section', None)

################################################################################# Titles #################################################################################

def GetTitles(section, url, startPage= '1', numOfPages= '1'): 
        print 'Proses penyenaraian tajuk cerita %s' % url
        pageUrl = url
        if int(startPage)> 1:
                pageUrl = url + '?page=' + startPage
        print pageUrl
        html = net.http_GET(pageUrl).content
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + 'page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content
                match = re.compile('<h2.+?href="(.+?)".+?>(.+?)<.+?src="(.+?)"', re.DOTALL).findall(html)
                for movieUrl, name, img in match:
                        addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': movieUrl}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png') 
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': '[COLOR blue][B][I]Next page...[/B][/I][/COLOR]'}, img=IconPath + 'next.png', fanart=FanartPath + 'fanart.png')
       	xbmcplugin.endOfDirectory(int(sys.argv[1]))

################################################################################# Episode #################################################################################

def GetEpisode(section, url, startPage= '1', numOfPages= '1'): 
        print 'Proses penyenaraian tajuk cerita %s' % url
        pageUrl = url
        if int(startPage)> 1:
                pageUrl = url + '?page=' + startPage
        print pageUrl
        html = net.http_GET(pageUrl).content
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + 'page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content
                match = re.compile('<h2.+?href="(.+?)".+?>(.+?)<.+?src="(.+?)"', re.DOTALL).findall(html)
                for movieUrl, name, img in match:
                        addon.add_directory({'mode': 'GetEpisodelinks', 'section': section, 'url': movieUrl}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png') 
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': '[COLOR blue][B][I]Next page...[/B][/I][/COLOR]'}, img=IconPath + 'next.png', fanart=FanartPath + 'fanart.png')
       	xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
############################################################################### Get Episodelinks #############################################################################################

def GetEpisodelinks(section, url):
        print 'GETLINKS FROM URL: '+url
        html = net.http_GET(url).content
        listitem = GetMediaInfo(html)
        content = html
        match = re.compile('<.+?href="(.+?)".+?>(.+?)<').findall(content)
        listitem = GetMediaInfo(content)
        for url, name in match:
                r = re.search('link=', content)
                if r: addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': url}, {'title':  name.strip()}, fanart=FanartPath + 'fanart.png')
                else: 
                       host = GetDomain(url)
                       if urlresolver.HostedMediaFile(url= url):
                             addon.add_directory({'mode': 'PlayVideo', 'url': url, 'listitem': listitem}, {'title':  host }, img=IconPath + 'play.png', fanart=FanartPath + 'fanart.png')
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

############################################################################### Get links #############################################################################################


def GetLinks(section, url):
        print 'GETLINKS FROM URL: '+url
        html = net.http_GET(url).content
        listitem = GetMediaInfo(html)
        content = html
        match = re.compile('href="(.+?)"').findall(content)
        listitem = GetMediaInfo(content)
        for url in match:
                host = GetDomain(url)
                if urlresolver.HostedMediaFile(url= url):
                        addon.add_directory({'mode': 'PlayVideo', 'url': url, 'listitem': listitem}, {'title':  host }, img=IconPath + 'play.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

############################################################################# Play Video #####################################################################################

def PlayVideo(url, listitem):
    try:
        print 'in PlayVideo %s' % url
        stream_url = urlresolver.HostedMediaFile(url).resolve()
        xbmc.Player().play(stream_url)
        addon.add_directory({'mode': 'help'}, {'title':  '[COLOR slategray][B]^^^ Press back ^^^[/B] [/COLOR]'},'','')
    except:
        xbmc.executebuiltin("XBMC.Notification([COLOR red][B]Sorry Link may have been removed ![/B][/COLOR],[COLOR lime][B]Please try a different link/host !![/B][/COLOR],7000,"")")


def GetDomain(url):
        tmp = re.compile('//(.+?)/').findall(url)
        domain = 'Unknown'
        if len(tmp) > 0 :
            domain = tmp[0].replace('www.', '')
        return domain

def GetMediaInfo(html):
        listitem = xbmcgui.ListItem()
        match = re.search('og:title" content="(.+?) \((.+?)\)', html)
        if match:
                print match.group(1) + ' : '  + match.group(2)
                listitem.setInfo('video', {'Title': match.group(1), 'Year': int(match.group(2)) } )
        return listitem

###################################################################### menus ####################################################################################################

def MainMenu():    #homescreen
        addon.add_directory({'mode': 'AcgMenu'}, {'title':  '[COLOR blue]ACG-TUBE[/COLOR] >>'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'Dfm2uMenu'}, {'title':  '[COLOR blue]DFM2U[/COLOR] >>'}, img=IconPath + 'dfm2uico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'ResolverSettings'}, {'title':  '[COLOR red]Resolver Settings[/COLOR]'}, img=IconPath + 'resolver.png', fanart=FanartPath + 'fanart.png')       
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
def AcgMenu():    #G
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/acgtube/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'ACG-TUBE'}, img=IconPath + 'acgico.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


def Dfm2uMenu():
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/movie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'DFM2U Movies'}, img=IconPath + 'dfm2uico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/telemovie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'DFM2U Telemovie'}, img=IconPath + 'dfm2uico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/drama/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'DFM2U Dramas'}, img=IconPath + 'dfm2uico.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/dfm2u/tvshow/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'DFM2U TV Show'}, img=IconPath + 'dfm2uico.png', fanart=FanartPath + 'fanart.png')                                          
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#################################################################################################################################################################################

if mode == 'main': 
	MainMenu()
elif mode == 'AcgMenu': 
    AcgMenu()
elif mode == 'Dfm2uMenu':
    Dfm2uMenu()
elif mode == 'GetTitles': 
	GetTitles(section, url, startPage, numOfPages)
elif mode == 'GetEpisode': 
	GetEpisode(section, url, startPage, numOfPages)
elif mode == 'GetEpisodelinks':
	GetEpisodelinks(section, url)        
elif mode == 'GetLinks':
	GetLinks(section, url)
elif mode == 'GetSearchQuery':
	GetSearchQuery()
elif mode == 'Search':
	Search(query)
elif mode == 'PlayVideo':
	PlayVideo(url, listitem)	
elif mode == 'ResolverSettings':
        urlresolver.display_settings()
xbmcplugin.endOfDirectory(int(sys.argv[1]))