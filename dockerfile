FROM python:3.12-slim

WORKDIR /app

RUN chown 1200:1200 /app

COPY bot.py .
COPY reel_scrape.py .

RUN pip3 install requests
RUN pip3 install python-telegram-bot==20.8

ENTRYPOINT [ "python3" ]

CMD [ "-u", "bot.py" ]
