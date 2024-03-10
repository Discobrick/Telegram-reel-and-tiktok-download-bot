import os
import re
import time
import logging as log
from datetime import datetime
import requests

def get_video_link_rapid_api(download_url):
    url = "https://social-media-video-downloader.p.rapidapi.com/smvd/get/all"

    querystring = {
        "url": download_url, "filename": "YTvideo"}

    headers = {
        "X-RapidAPI-Key": os.environ.get('RAPID_API_KEY'),
        "X-RapidAPI-Host": "social-media-video-downloader.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    for item in response.json()['links']:
        if item['quality'] == 'sd_360p' or item['quality'] == 'hd' or item['quality'] == 'original':
            print(item)
            return item['link']



def download_reel(download_url, from_user):
    video_url = get_video_url(download_url)
    r = requests.get(video_url, timeout=300, allow_redirects=True)
    file_path = '/app/' + from_user + \
        datetime.now().strftime("%d%m%Y%H%M%S") + '.mp4'
    open(file_path, 'wb').write(r.content)
    return file_path
 

def get_video_url(download_url):
    for i in range(10):
        time.sleep(i)
        try:
            video_url = get_video_link_rapid_api(download_url)
        except Exception as e:
            if i < 10 - 1:
                continue
            else:
                log.error(e)
                raise
        else:
            break
    return video_url
