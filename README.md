# Telegram-reel-and-tiktok-download-bot


A simple bot that uses Selenium,Firefox,Ublock and https://snapsave.app

A newer .xpi file can be retrieved from their oficial github releases here https://github.com/gorhill/uBlock/releases


To run the bot edit the .env file with your own API key and run the following command
```
docker compose up --build -d
```
Since the image that I'm using is for Selenium Grid with Firefox the docker run command is just the default docker run you'd get when following the quickstart guide in their github repo

Next run the following command to run the bot.py inside the container

```
docker compose exec botty_mcbotface python3 bot.py -d
```

Added an option to have the bot post videos to a certain topic.
To configure a topic simply enter the following text into the topic you want to be the destination for all the videos 
```
initCurrentTopicAsMemeBotTopic
```

To reset this setting simply send the following message in the active topic
```
resetMemeTopic
``` 