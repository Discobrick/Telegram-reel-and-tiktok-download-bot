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
2. Set up your bot API key in environment variables
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
initCurrentTopicAsMemeBotTopic
```

- To reset this setting and return to the default behavior:
```
clearMemeBotTopic
```

### Video Descriptions

Toggle whether to include video descriptions with downloads:

```
optInDescription
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

### Error Handling

The bot logs failed download attempts and can generate reports with the `/report` command.

## Notes

- When processing links, the bot will react with emojis to show progress
- The original message containing links will be deleted after processing
- Videos are temporarily stored and automatically cleaned up after sending
