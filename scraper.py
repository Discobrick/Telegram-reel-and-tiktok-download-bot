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

# Telegram's bot API refuses uploads larger than 50 MB
MAX_FILESIZE = 50 * 1024 * 1024

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
        f"{str(uuid.uuid4())}.mp4"
    )

    ydl_opts = {
        'outtmpl': file_path,
        # Abort early instead of pulling gigabytes we'd only reject at upload time
        'max_filesize': MAX_FILESIZE,
        'final_ext': 'mp4',
        'format_sort': ['vcodec:h264',
                        'lang',
                        'quality',
                        'res',
                        'fps',
                        'hdr:12',
                        'acodec:aac'],
        'merge_output_format': 'mp4',
        'postprocessors': [{'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}]
    }

    video_info = download_with_dlp(download_url, ydl_opts, get_description)

    # yt_dlp skips oversized videos quietly rather than raising, so no file means
    # it hit max_filesize (or the remux produced nothing usable)
    if not os.path.exists(file_path):
        raise ValueError(
            f"No video file produced - it likely exceeds the {MAX_FILESIZE // (1024 * 1024)} MB limit"
        )

    if get_description:
        return file_path, video_info
    return file_path

def download_with_dlp(download_url, opts, get_description=False):
    """Download the video using yt_dlp with the given options."""
    try:
        # Single pass: extract_info with download=True returns the metadata too
        with yt_dlp.YoutubeDL(opts) as ydl:
            info_dict = ydl.extract_info(download_url, download=True)

        if not get_description:
            return {}

        return {
            'title': info_dict.get('title', 'No title available'),
            'description': info_dict.get('description', 'No description available'),
            'uploader': info_dict.get('uploader', 'Unknown uploader'),
            'upload_date': info_dict.get('upload_date', 'Unknown date'),
            'view_count': info_dict.get('view_count', 'Unknown views'),
        }
    except yt_dlp.utils.DownloadError as e:
        raise ValueError(f"Download failed: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {str(e)}") from e
