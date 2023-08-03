# Telegram-reel-and-tiktok-download-bot


A simple bot that uses Selenium,Firefox,Ublock and https://snapsave.app

For it to work you need to add your telegram bot token in bot.py:13 and a path to Ublock .xpi file in reelScrape.py:16

A newer .xpi file can be retrieved from their oficial github releases here https://github.com/gorhill/uBlock/releases


First build the image with this command edit the docker file to 
```
docker build -t "botimage:latest" -f ./Dockerfile .
```

Second run the container with the command below

```
docker run --hostname=16ad92754358 --user=1200 --env=BOT_API_KEY=<INSERT_YOUR_BOT_API_KEY_HERE> --env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --env=SE_SCREEN_HEIGHT=1020 --env=SE_VNC_PORT=5900 --env=SE_SCREEN_WIDTH=1360 --env=SE_START_NO_VNC=true --env=WEBSOCKIFY_VERSION=0.11.0 --env=SE_SCREEN_DEPTH=24 --env=SE_SCREEN_DPI=96 --env=SE_NODE_SESSION_TIMEOUT=300 --env=HOME=/home/seluser --env=LANG_WHICH=en --env=SE_START_XVFB=true --env=GENERATE_CONFIG=true --env=DEBCONF_NONINTERACTIVE_SEEN=true --env=LANG=en_US.UTF-8 --env=SE_START_VNC=true --env=DBUS_SESSION_BUS_ADDRESS=/dev/null --env=SE_RELAX_CHECKS=true --env=TZ=UTC --env=NOVNC_VERSION=1.4.0 --env=SE_DRAIN_AFTER_SESSION_COUNT=0 --env=SE_NODE_OVERRIDE_MAX_SESSIONS=false --env=DEBIAN_FRONTEND=noninteractive --env=SE_BIND_HOST=false --env=ENCODING=UTF-8 --env=LANGUAGE=en_US.UTF-8 --env=DISPLAY_NUM=99 --env=CONFIG_FILE=/opt/selenium/config.toml --env=SE_NODE_MAX_SESSIONS=1 --env=LANG_WHERE=US --env=SE_NO_VNC_PORT=7900 --env=DISPLAY=:99.0 --workdir=/app -p 4444:4444 -p 7900:7900 --restart=unless-stopped --label='authors=' --label='org.opencontainers.image.ref.name=ubuntu' --label='org.opencontainers.image.version=20.04' --runtime=runc --name botty_mcbotface -d botimage:latest
```
Since the image that I'm using is for Selenium Grid with Firefox the docker run command is just the default docker run you'd get when following the quickstart guide in their github repo

Next run the following command to run the bot.py inside the container

```
docker exec botty_mcbotface python3 bot.py &
```
