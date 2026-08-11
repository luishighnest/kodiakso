import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import re

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def get_string(string_id):
    return ADDON.getLocalizedString(string_id)

def get_m3u_url():
    return ADDON.getSetting('m3u_url')

def parse_m3u(content):
    items = []
    lines = content.splitlines()
    
    current_item = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#KODIPROP:'):
            prop_str = line.replace('#KODIPROP:', '')
            if '=' in prop_str:
                key, val = prop_str.split('=', 1)
                if 'properties' not in current_item:
                    current_item['properties'] = {}
                current_item['properties'][key] = val
                
        elif line.startswith('#EXTINF:'):
            # Parse title
            title_match = re.search(r',(.*)$', line)
            current_item['title'] = title_match.group(1).strip() if title_match else 'Sconosciuto'
            
            # Parse logo
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            if logo_match:
                current_item['logo'] = logo_match.group(1)
                
            # Parse provider
            provider_match = re.search(r'tvg-provider="([^"]+)"', line)
            if provider_match:
                current_item['provider'] = provider_match.group(1)
                
        elif not line.startswith('#'):
            # This is the URL
            current_item['url'] = line
            items.append(current_item)
            current_item = {}
            
    return items

def build_url(query):
    return BASE_URL + '?' + urllib.parse.urlencode(query)

def list_channels():
    m3u_url = get_m3u_url()
    
    if not m3u_url:
        xbmcgui.Dialog().ok("Dynamic MPD", get_string(30002))
        xbmcplugin.endOfDirectory(HANDLE)
        return
        
    try:
        response = requests.get(m3u_url, timeout=10)
        response.raise_for_status()
        items = parse_m3u(response.text)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)
        xbmcplugin.endOfDirectory(HANDLE)
        return
        
    for item in items:
        title = item.get('title', 'Unknown')
        url = item.get('url', '')
        
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'title': title})
        
        if 'logo' in item:
            list_item.setArt({'thumb': item['logo'], 'icon': item['logo']})
            
        # Set inputstream.adaptive properties
        list_item.setProperty('isPlayable', 'true')
        
        if 'properties' in item:
            for key, val in item['properties'].items():
                list_item.setProperty(key, val)
                
        play_url = build_url({'action': 'play', 'video_url': url})
        
        # Add to directory
        is_folder = False
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=play_url, listitem=list_item, isFolder=is_folder)
        
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(url):
    # Riproduce il video. Le proprietà di inputstream sono passate direttamente se le ritrovo dall'URL,
    # Ma in realtà Kodi le ricorda dal ListItem della directory. 
    # Per sicurezza le estraggo nuovamente o mi fido del ListItem generato da list_channels.
    # In Kodi, quando un elemento ha setProperty('isPlayable', 'true') e setProperty per inputstream,
    # si può semplicemente passare xbmcplugin.setResolvedUrl
    
    list_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=list_item)


def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    
    if params:
        if params['action'] == 'play':
            play_video(params['video_url'])
        else:
            raise ValueError(f"Invalid paramstring: {paramstring}!")
    else:
        list_channels()

if __name__ == '__main__':
    router(sys.argv[2][1:])
