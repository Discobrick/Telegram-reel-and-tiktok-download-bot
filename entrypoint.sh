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
    # Dropping the extra does not remove an already-installed curl_cffi from the volume
    pip3 uninstall --quiet --yes curl_cffi >/dev/null 2>&1 || true
    # No curl-cffi: yt-dlp caps that extra at <0.16, and TikTok rejects the TLS
    # fingerprints those versions send. yt-dlp impersonates whenever curl_cffi is
    # importable, so the only way off that path is to not install it.
    # ponytail: revisit once yt-dlp allows curl-cffi >=0.16
    if ! pip3 install --quiet --user --upgrade --pre "yt-dlp[default]"; then
        echo "yt-dlp update failed, continuing with the version baked into the image"
    fi
fi

python3 -c "import yt_dlp; print('yt-dlp', yt_dlp.version.__version__)"

exec python3 -u bot.py
