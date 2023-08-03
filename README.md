# Telegram-reel-and-tiktok-download-bot


A simple bot that uses Selenium,Firefox,Ublock and https://snapsave.app

A newer .xpi file can be retrieved from their oficial github releases here https://github.com/gorhill/uBlock/releases


First build the image with this command edit the docker file to 
```
docker build -t "botimage:latest" -f ./Dockerfile .
```

Second run the container with the command below

```
docker run --hostname=16ad92754358 --user=1200 --env-file=.env --workdir=/app -p 4444:4444 -p 7900:7900 --restart=unless-stopped --label='authors=' --label='org.opencontainers.image.ref.name=ubuntu' --label='org.opencontainers.image.version=20.04' --runtime=runc --name botty_mcbotface -d botimage:latest
```
Since the image that I'm using is for Selenium Grid with Firefox the docker run command is just the default docker run you'd get when following the quickstart guide in their github repo

Next run the following command to run the bot.py inside the container

```
docker exec botty_mcbotface python3 bot.py &
```
