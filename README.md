# Telegram-reel-and-tiktok-download-bot

A Telegram bot that automatically downloads and shares videos from multiple social media platforms.

## Supported Platforms

- Instagram Reels
- TikTok
- Twitter/X
- YouTube Shorts
- Facebook Reels
- 9GAG

## Setup

1. Clone repo
2. Set up your bot API key in environment variable:
```
    echo "BOT_API_KEY=123:abc" > .env
```
3. Run the command below
4. Done

```
docker compose up --build -d
```

## Features

### Topic Management

Configure the bot to post videos to a specific topic:

- To set a topic as the destination for all videos:
```
/settopic
```

- To reset this setting and return to the default behavior:
```
/cleartopic
```

### Video Descriptions

Toggle whether to include video descriptions with downloads:

```
/toggledesc
```

This will show detailed information about the video including:
- Video title
- Uploader name
- Upload date
- View count
- Video description (truncated if too long)

### Original Link

Toggle whether the original link is included with each download:

```
/togglelink
```

The link is placed near the top of the caption so it stays visible even when a long
description follows. This setting is independent of `/toggledesc` — you can enable
either, both, or neither.

### Silent Failure Mode

Toggle whether the bot gives any feedback when a download fails:

```
/togglesilent
```

When enabled, failed downloads produce no reaction or error message — the bot stays completely silent. Errors are still logged internally. Useful for busy chats where failure noise is unwanted.

### Facebook Marketplace

Links that resolve to Facebook Marketplace listings are automatically detected and silently ignored. No error reaction is shown.

### Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information and list of supported platforms
- `/report` - Generate a report of failed downloads
- `/toggledesc` - Toggle video descriptions on/off
- `/togglelink` - Toggle including the original link on/off
- `/togglesilent` - Toggle silent failure mode (no error reactions/messages)
- `/toggleerrors` - Toggle message-deletion error reports on/off (chat-wide)
- `/settopic` - Set current chat/topic as target for downloads
- `/cleartopic` - Clear target chat/topic setting

### Persistent Preferences

The bot now stores user preferences persistently across restarts:
- User preferences are saved in a JSON file
- Preferences are maintained per user and per chat
- Settings persist even when the bot is restarted or the container is rebuilt
- No additional setup is required as the Docker configuration already includes volume mapping

### Legacy Commands

The following commands are still supported for backward compatibility:
```
initCurrentTopicAsMemeBotTopic  # Same as /settopic
clearMemeBotTopic               # Same as /cleartopic
optInDescription                # Same as /toggledesc
```

### Error Handling

The bot logs failed download attempts and can generate reports with the `/report` command.

## Notes

- When processing links, the bot will react with emojis to show progress
- The original message is deleted only when every link in it was downloaded and sent
  successfully — if any link fails or is skipped, the message is kept so nothing is lost
- Videos larger than 50 MB are rejected: Telegram's bot API will not accept them
- Videos are temporarily stored and automatically cleaned up after sending
- User preferences are stored in `/data/preferences.json` and persist across container restarts
- `error.log` rotates at 5 MB (3 backups kept), so the data volume will not fill up

## Maintenance

yt-dlp breaks whenever the supported sites change their extractors, which happens more
often than this image gets rebuilt. The container upgrades yt-dlp on every start into the
persistent volume, so a plain `docker compose restart` is enough to pick up a fix:

```
docker compose restart
```

To pin yt-dlp to whatever the image was built with, set `YTDLP_AUTO_UPDATE=0` in the
environment. If an update ever ships a regression, drop the upgraded copy to fall back to
the image's version (this leaves preferences untouched):

```
docker compose run --rm --entrypoint sh botty_mcbotface -c 'rm -rf /data/pip'
docker compose up -d
```

## Development

The caption building and chunking logic has a self-check that runs without any
dependencies installed:

```
python3 test_caption.py
```