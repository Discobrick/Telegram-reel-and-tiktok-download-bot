FROM python:3.12-slim

WORKDIR /app

RUN sudo apt-get update
RUN sudo apt-get upgrade -y
RUN sudo apt-get install python3-pip -y
RUN sudo apt-get install screen -y

COPY bot.py .
COPY reel_scrape.py .

RUN pip3 install python-telegram-bot==20.8