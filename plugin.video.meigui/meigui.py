# -*- coding:utf-8 -*-
import re
import requests,urllib
import xbmcplugin, xbmcgui

# 【一些经常用到的变量】
_handle=int(sys.argv[1]) #当前句柄
_pluginurl = sys.argv[0] #当前地址 plugin.video.video/
_url = sys.argv[2] #取地址?号后面的
_site = 'http://www.haoav59.com'
_site_encoding = 'gb2312'
_black_words = u'幼女,儿童,学生,未成年'

print('malimaliao:(' + str(_handle) + ')' + _pluginurl)

UA_head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
    'referer': 'http://www.haoav59.com',
}

# 【获取频道栏目列表】
def load_typelist(dianying_url):
    print('TO HOME URL:' + dianying_url)
    res = requests.get(dianying_url, headers=UA_head)
    res.encoding = _site_encoding
    html_code = res.text
    gz = re.compile(r'<li><a.href="?(.+?).html"?>(.+?)</a></li>')
    types = gz.findall(html_code)
    if len(types) > 0:
        for type in types:
            type_name = type[1]
            # KODI代码嵌入开始
            #因为源站点不包含?，而插件地址必须包含?，构造kodi识别的?koditype=/list/index29
            kodi_typeurl= '?koditype=' + type[0] + '.html'
            print(kodi_typeurl)
            if type_name in _black_words:
                continue
            else:
                listitem = xbmcgui.ListItem(type_name)
                xbmcplugin.addDirectoryItem(_handle, _pluginurl + kodi_typeurl, listitem, True)
            # KODI代码嵌入完毕
    else:
        print('无法获取电影分类列表')
# 【获取栏目电影列表】
def load_videolist(dianying_type_url):
    print('TO URL:'+dianying_type_url)
    res = requests.get(dianying_type_url, headers=UA_head)
    res.encoding = _site_encoding
    htmlcode = res.text
    GZ_videos = re.compile(r'<a.href="(.+?)".class="pic".+<img.src="(.+?)".+</a>\s*<a.+txt.+>(.+?)</a>')
    videos = GZ_videos.findall(htmlcode)
    if len(videos) > 0:
        for video in videos:
            # kodi菜单传递后_url获取的则是?之后的内容
            kodi_vurl = '?kodivideo=' + video[0]
            v_image = video[1]
            v_title = video[2]
            #KODI代码嵌入开始
            listitem=xbmcgui.ListItem(v_title, iconImage=v_image, thumbnailImage=v_image)
            xbmcplugin.addDirectoryItem(_handle, _pluginurl + kodi_vurl, listitem, True)
            #KODI代码嵌入完毕
    else:
        print('暂时无法获取到本栏目下的电影列表')

# 【获取电影信息】
def load_videoinfo(dianying_detail_url):
    print('TO VIDEO URL:'+dianying_detail_url)
    videoinfo = {}
    res = requests.get(dianying_detail_url, headers=UA_head)
    res.encoding = _site_encoding
    htmlcode_info = res.text
    #play title
    gz_title = re.compile(r'T2">(.+?)<div')
    ts = gz_title.findall(htmlcode_info)
    if len(ts) > 0:
        for t in ts:
            videoinfo['title'] = t
    else:
        videoinfo['title'] = u'资源播放'
    #playlist
    GZ_playlists = re.compile(r'video=\["(.+?)->video')
    playlists = GZ_playlists.findall(htmlcode_info)
    if len(playlists) > 0:
        playurllist = {}
        i = 0
        for play in playlists:
            print('mp4:' + play)
            print('mp40:' + play[0])
            #当正则子匹配只需要1个的时候，在for循环里不要加[0]索引
            i = i + 1
            play_title = 'play:' + str(i)
            playurllist[play_title] = play
        print(playurllist)
        videoinfo['playlist'] = playurllist
    else:
        print('本视频暂无播放地址')
        videoinfo['playlist'] ={}
    return videoinfo


#当前为首页，为用户【建立主栏目菜单】
if _url == '':
    # 载入分类列表，并生成分类栏目菜单
    load_typelist(_site)
#当前为栏目列表，提取typeid，为用户【建立视频列表】
if 'koditype=' in _url:
    _gourl = urllib.unquote(_url)#URL解码
    print('选择分类菜单：' + _gourl)
    GZ_type = re.compile(r'koditype=(.+?)$')  # 栏目规则
    gourls = GZ_type.findall(_gourl)
    if len(gourls) > 0:
        for gourl in gourls:
            load_videolist(_site + gourl)
    else:
        print('无法提取koditype')

#当前为视频标题URL，提取detail id，为用户【载入视频信息】
if 'kodivideo=' in _url:
    _gourl = urllib.unquote(_url)  # URL解码
    print('选择视频菜单：' + _gourl)
    GZ_vid = re.compile(r'kodivideo=(.+?)$')  # 栏目规则
    vids = GZ_vid.findall(_gourl)
    if len(vids) > 0:
        for vid_url in vids:
            #载入指定vid的视频信息
            vid_url = vid_url.replace('/view/', '/player/')
            videodata = load_videoinfo(_site + vid_url)
            movie_title = videodata['title']
            movie_playlist = videodata['playlist']
            for playurl in videodata['playlist'].items():
                print(playurl[0] + playurl[1])
                listitem = xbmcgui.ListItem(movie_title + playurl[0])
                xbmcplugin.addDirectoryItem(_handle, playurl[1], listitem, False)
    else:
        print('无法提取kodivideo')

# 目录构建完了，显示吧
xbmcplugin.endOfDirectory(_handle) #退出菜单布局
