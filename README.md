# Telegram-reel-and-tiktok-download-bot


A simple bot that uses Selenium,Firefox,Ublock and https://snapsave.app

A newer .xpi file can be retrieved from their oficial github releases here https://github.com/gorhill/uBlock/releases


To run the bot edit the .env file with your own API key and run the following command
```
ducker compose up --build -d
```
Since the image that I'm using is for Selenium Grid with Firefox the docker run command is just the default docker run you'd get when following the quickstart guide in their github repo

Next run the following command to run the bot.py inside the container

```
docker compose exec -d botty_mcbotface python3 bot.py
```
