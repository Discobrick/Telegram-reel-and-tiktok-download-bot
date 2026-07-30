FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg npm && \
    npm install -g deno && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir requests python-telegram-bot==21.9 -U --pre "yt-dlp[default,curl-cffi]"

# Entrypoint upgrades yt-dlp into here on start; /data is the persistent volume
ENV PYTHONUSERBASE=/data/pip

# Create data directory and log files with proper permissions
RUN mkdir -p /data/pip && \
    echo '{}' > /data/preferences.json && \
    touch /data/error.log && \
    touch /data/failed_links.log && \
    chown -R 1200:1200 /app && \
    chown -R 1200:1200 /data && \
    chmod 755 /data && \
    chmod 666 /data/preferences.json && \
    chmod 666 /data/error.log && \
    chmod 666 /data/failed_links.log && \
    # Create yt-dlp cache directory with proper permissions
    mkdir -p /.cache/yt-dlp && \
    chmod -R 777 /.cache

COPY bot.py .
COPY scraper.py .
COPY --chmod=755 entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]
