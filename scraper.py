from datetime import datetime
import yt_dlp

def download_reel(download_url,from_user):
    return download_reel_dlp(download_url,from_user)

def download_reel_dlp(download_url, from_user):
    file_path = '/app/' + datetime.now().strftime("%d%m%Y%H%M%S") + ".mp4"
    ydl_opts = {
        # "format": "best[ext=mp4]",
        'outtmpl':file_path,
        # 'final_ext': 'mp4',
        'format': 'bestvideo[vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'format_sort': ['res', 'ext:mp4:m4a','vcodec:h264'],
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
    }
    download_with_dlp(download_url,ydl_opts)
    return file_path
        
def download_with_dlp(download_url,opts):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download(download_url)

