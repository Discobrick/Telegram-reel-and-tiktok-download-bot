FROM python:3.12-slim

WORKDIR /app

RUN chown 1200:1200 /app

COPY bot.py .
COPY scraper.py .

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install requests python-telegram-bot==21.9 -U --pre "yt-dlp[default]"

ENTRYPOINT ["python3"]

CMD ["-u", "bot.py"]