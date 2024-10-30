FROM python:3.12-slim

WORKDIR /app

RUN chown 1200:1200 /app

COPY bot.py .
COPY scraper.py .

RUN apt-get update \
  && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install requests
RUN pip3 install python-telegram-bot==20.8
RUN pip3 install -U --pre "yt-dlp[default]"

ENTRYPOINT [ "python3" ]

CMD [ "-u", "bot.py" ]
