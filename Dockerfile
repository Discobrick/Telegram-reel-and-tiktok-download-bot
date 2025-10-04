FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install requests python-telegram-bot==21.9 -U --pre "yt-dlp[default]"

# Create data directory and log files with proper permissions
RUN mkdir -p /data && \
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

ENTRYPOINT ["python3"]

CMD ["-u", "bot.py"]
