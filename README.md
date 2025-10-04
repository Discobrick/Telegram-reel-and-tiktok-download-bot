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

### Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information and list of supported platforms
- `/report` - Generate a report of failed downloads
- `/toggledesc` - Toggle video descriptions on/off
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
- The original message containing links will be deleted after processing
- Videos are temporarily stored and automatically cleaned up after sending
- User preferences are stored in `/app/data/preferences.json` and persist across container restarts