import m3u8
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook as tqdm
import subprocess

st_url = input("stream URL: ")
video_name = input("A name for output video: ")
output = video_name + '.mp4'

sess = requests.Session()
r = sess.get(st_url)
soup = BeautifulSoup(r.content, 'html5lib')
video_id = soup.find('video', attrs={'id': 'playlistPlayer'})['data-video-id']
account_id = soup.find('video', attrs={'id': 'playlistPlayer'})['data-account']

url = "https://secure.brightcove.com/services/mobile/streaming/index/master.m3u8"

params = {
    'videoId': video_id,
    'pubId': account_id,
    'secure': True
}

r = sess.get(url, params=params)

m3u8_master = m3u8.loads(r.text)
m3u8_playlist_uris = [playlist['uri'] for playlist in m3u8_master.data['playlists']]
playlist_uri = m3u8_playlist_uris[0]

r = sess.get(playlist_uri)
playlist = m3u8.loads(r.text)
m3u8_segment_uris = [segment['uri'] for segment in playlist.data['segments']]

with open("video.ts", 'wb') as f:
    for segment_uri in tqdm(m3u8_segment_uris):
        r = sess.get(segment_uri)
        f.write(r.content)

subprocess.run(['ffmpeg', '-i', 'video.ts', output])
