#!/bin/sh
# yt-dlp breaks whenever the sites change their extractors, which is far more
# often than this image gets rebuilt. Upgrade on start into PYTHONUSERBASE
# (/data, the persistent volume) so it survives restarts without a rebuild.
# Set YTDLP_AUTO_UPDATE=0 to pin to whatever the image shipped with.
set -e

if [ "${YTDLP_AUTO_UPDATE:-1}" = "1" ]; then
    # An existing named volume predates the image's /data/pip, and Docker only
    # seeds a volume when it is empty, so create it here too
    mkdir -p "${PYTHONUSERBASE:-/data/pip}"
    echo "Updating yt-dlp..."
    if ! pip3 install --quiet --user --upgrade --pre "yt-dlp[default,curl-cffi]"; then
        echo "yt-dlp update failed, continuing with the version baked into the image"
    fi
fi

python3 -c "import yt_dlp; print('yt-dlp', yt_dlp.version.__version__)"

exec python3 -u bot.py
