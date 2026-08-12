import sys
import urllib.request
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmcaddon

# Recupera le info dell'addon
addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
base_url = sys.argv[0]

# --- INSERISCI QUI L'URL RAW DELLA TUA PLAYLIST M3U SU GITHUB ---
M3U_URL = "https://raw.githubusercontent.com/luishighnest/kodiakso/main/playlist.m3u"

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def list_channels():
    # Scarica il file M3U
    try:
        req = urllib.request.Request(M3U_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            m3u_content = response.read().decode('utf-8').splitlines()
    except Exception as e:
        xbmcgui.Dialog().notification('Errore', f'Impossibile caricare M3U: {str(e)}', xbmcgui.NOTIFICATION_ERROR)
        return

    channels = []
    current_channel = {}
    
    # Semplice parsing M3U
    for line in m3u_content:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            # Cerca il nome del canale (dopo la virgola)
            parts = line.split(',')
            if len(parts) > 1:
                current_channel['name'] = parts[-1].strip()
            else:
                current_channel['name'] = 'Sconosciuto'
        elif line and not line.startswith('#'):
            current_channel['url'] = line
            channels.append(current_channel)
            current_channel = {}

    # Crea gli item in Kodi
    for channel in channels:
        name = channel.get('name', 'Senza Nome')
        url = channel.get('url', '')
        
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {'title': name})
        li.setProperty('IsPlayable', 'true')
        
        # URL per riprodurre il video
        play_url = build_url({'action': 'play', 'video': url})
        
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=li, isFolder=False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def play_video(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    
    if params:
        if params['action'] == 'play':
            play_video(params['video'])
        else:
            raise ValueError('Azione non valida: {}'.format(params['action']))
    else:
        list_channels()

if __name__ == '__main__':
    router(sys.argv[2][1:])
