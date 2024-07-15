import os
import time
import logging as log
from datetime import datetime
import requests
import yt_dlp
import re

def get_video_link_rapid_api(download_url):
    url = "https://social-media-video-downloader.p.rapidapi.com/smvd/get/all"
    querystring = {
        "url": download_url, "filename": "video"}

    headers = {
        "X-RapidAPI-Key": os.environ.get('RAPID_API_KEY'),
        "X-RapidAPI-Host": "social-media-video-downloader.p.rapidapi.com"
    }

    link_identifiers = os.environ.get('RAPID_API_LINK_IDENTIFIED').split(";")
    response = requests.get(url, headers=headers, params=querystring)
    
    
    if re.match(r"(.*www\.facebook\.com\/reel.*)|(.*fb\.watch\/.*)|(.*www\.facebook\.com\/share.*)",download_url):        
        return response.json()['links'][0]['link']
    
    if re.match(r".*.tiktok.com\/",download_url):        
        return response.json()['links'][0]['link']
    
    
    # for item in response.json()['links']:
    #     if item['quality'] in link_identifiers:
    #         return item['link']
        
        
def download_with_dlp(download_url,opts):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download(download_url)

def download_reel(download_url,from_user):
    if re.match(r"(.*.tiktok.com\/)|(.*www\.facebook\.com\/reel.*)|(.*fb\.watch\/.*)|(.*www\.facebook\.com\/share.*)",download_url):
        return download_reel_rapid(download_url,from_user)
    if re.match(r"(.*9gag\.com\/gag\/.*)|(.*x\.com\/.*\/status\/.*)|(.*www\.instagram\.com\/reel.*)|(.*(www\.|)youtube\.com\/shorts\/.*)",download_url):
        return download_reel_dlp(download_url,from_user)


def download_reel_rapid(download_url, from_user):
    video_url = get_video_url(download_url)
    r = requests.get(video_url, timeout=300, allow_redirects=True)
    file_path = '/app/' + from_user + \
        datetime.now().strftime("%d%m%Y%H%M%S") + '.mp4'
    open(file_path, 'wb').write(r.content)
    return file_path


def download_reel_dlp(download_url, from_user):
    file_path = '/app/' + datetime.now().strftime("%d%m%Y%H%M%S") + ".mp4"
    ydl_opts = {
        # "format": "best[ext=mp4]",
        'outtmpl':file_path,
        'final_ext': 'mp4',
        'format_sort': ['res', 'ext:mp4:m4a'],
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
    }
    download_with_dlp(download_url,ydl_opts)
    return file_path

def get_video_url(download_url):
    for i in range(1):
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
