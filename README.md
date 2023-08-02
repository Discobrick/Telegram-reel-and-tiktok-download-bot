# Telegram-reel-and-tiktok-download-bot


A simple bot that uses Selenium,Firefox,Ublock and https://snapsave.app

For it to work you need to add your telegram bot token in bot.py:13 and a path to Ublock .xpi file in reelScrape.py:16

A new .xpi file can be retrieved from their oficial github releases here https://github.com/gorhill/uBlock/releases

To launch it in docker you need to build the image and then run it with the following arguments

```
docker run --hostname=16ad92754358 --user=1200 --mac-address=02:42:ac:11:00:02 --env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --env=SE_SCREEN_HEIGHT=1020 --env=SE_VNC_PORT=5900 --env=SE_SCREEN_WIDTH=1360 --env=SE_START_NO_VNC=true --env=BOT_API_KEY=<YOUR_BOT_API_KEY> --env=WEBSOCKIFY_VERSION=0.11.0 --env=SE_SCREEN_DEPTH=24 --env=SE_SCREEN_DPI=96 --env=SE_NODE_SESSION_TIMEOUT=300 --env=HOME=/home/seluser --env=LANG_WHICH=en --env=SE_START_XVFB=true --env=GENERATE_CONFIG=true --env=DEBCONF_NONINTERACTIVE_SEEN=true --env=LANG=en_US.UTF-8 --env=SE_START_VNC=true --env=DBUS_SESSION_BUS_ADDRESS=/dev/null --env=SE_RELAX_CHECKS=true --env=TZ=UTC --env=NOVNC_VERSION=1.4.0 --env=SE_DRAIN_AFTER_SESSION_COUNT=0 --env=SE_NODE_OVERRIDE_MAX_SESSIONS=false --env=DEBIAN_FRONTEND=noninteractive --env=SE_BIND_HOST=false --env=ENCODING=UTF-8 --env=LANGUAGE=en_US.UTF-8 --env=DISPLAY_NUM=99 --env=CONFIG_FILE=/opt/selenium/config.toml --env=SE_NODE_MAX_SESSIONS=1 --env=LANG_WHERE=US --env=SE_NO_VNC_PORT=7900 --env=DISPLAY=:99.0 --workdir=/app/Telegram-reel-and-tiktok-download-bot -p 4444:4444 -p 7900:7900 --restart=no --label='authors=' --label='org.opencontainers.image.ref.name=ubuntu' --label='org.opencontainers.image.version=20.04' --runtime=runc -d <IMAGE_ID>
```

