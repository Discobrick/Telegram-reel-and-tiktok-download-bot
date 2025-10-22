"""
This module provides functions to download reels using yt_dlp.

Functions:
    download_reel(download_url): Download a reel using the provided URL.
    download_reel_dlp(download_url): Download a reel using yt_dlp with specified options.
    download_with_dlp(download_url, opts): Download the video using yt_dlp with the given options.
"""
from datetime import datetime
import os
import uuid

import yt_dlp

def download_reel(download_url, get_description=False):
    """Download a reel using the provided URL and username."""
    return download_reel_dlp(download_url, get_description)

def download_reel_dlp(download_url, get_description=False):
    """Download a reel using yt_dlp with specified options."""
    # Create a temp directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Use os.path.join for platform-independent path handling
    file_path = os.path.join(
        temp_dir,
        f"{datetime.now().strftime('%d%m%Y%H%M%S')}{str(uuid.uuid4())[:8]}.mp4"
    )

    ydl_opts = {
        'outtmpl': file_path,
        'format': 'bestvideo[vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'format_sort': ['res', 'ext:mp4:m4a', 'vcodec:h264'],
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'
    }

    video_info = download_with_dlp(download_url, ydl_opts, get_description)

    if get_description:
        return file_path, video_info
    return file_path

def download_with_dlp(download_url, opts, get_description=False):
    """Download the video using yt_dlp with the given options."""
    try:
        video_info = {}
        if get_description:
            # First extract info without downloading
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info_dict = ydl.extract_info(download_url, download=False)

                # Get title, description, uploader if available
                video_info['title'] = info_dict.get('title', 'No title available')
                video_info['description'] = info_dict.get('description', 'No description available')
                video_info['uploader'] = info_dict.get('uploader', 'Unknown uploader')
                video_info['upload_date'] = info_dict.get('upload_date', 'Unknown date')
                video_info['view_count'] = info_dict.get('view_count', 'Unknown views')

        # Now download the video
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([download_url])

        return video_info
    except yt_dlp.utils.DownloadError as e:
        raise ValueError(f"Download failed: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {str(e)}") from e
