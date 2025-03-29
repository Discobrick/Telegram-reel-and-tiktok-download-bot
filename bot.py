import logging as log
import os
import traceback
from telegram import Update, InputMediaVideo
from telegram import ReactionTypeEmoji
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler


from scraper import download_reel
import re

# Configure logging to file and console
log.basicConfig(
    level=log.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        log.FileHandler('error.log'),
        log.StreamHandler()
    ]
)

logger = log.getLogger(__name__)

# Store preferences by chat_id and user_id
# Format: preferences[chat_id][user_id] = {'show_description': bool, 'target_chat_id': int, ...}
preferences = {}

def get_user_prefs(chat_id, user_id):
    """Get user preferences for a specific chat."""
    if chat_id not in preferences:
        preferences[chat_id] = {}
    
    if user_id not in preferences[chat_id]:
        preferences[chat_id][user_id] = {}
    
    return preferences[chat_id][user_id]

async def toggle_description(update: Update, context) -> None:
    """Toggle showing descriptions for videos."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    user_prefs = get_user_prefs(chat_id, user_id)
    
    # Toggle the preference
    current_preference = user_prefs.get('show_description', False)
    user_prefs['show_description'] = not current_preference
    
    # Confirm to the user
    status = "enabled" if user_prefs['show_description'] else "disabled"
    await update.message.reply_text(f"Video descriptions are now {status} for your downloads in this chat.")
    logger.info(f"User {user_id} in chat {chat_id} set description preference to {status}")

async def set_topic_channel(update: Update, context) -> None:
    """Set current topic/channel as target for video downloads."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message_thread_id = update.effective_message.message_thread_id if hasattr(update.effective_message, 'message_thread_id') else None
    
    user_prefs = get_user_prefs(chat_id, user_id)
    
    # Save the target channel/topic information
    user_prefs['target_chat_id'] = chat_id
    user_prefs['target_topic_id'] = message_thread_id
    
    # Create confirmation message based on whether it's a topic or just a chat
    if message_thread_id:
        await update.message.reply_text("✅ This topic has been set as your target for video downloads.")
        logger.info(f"User {user_id} in chat {chat_id} set topic {message_thread_id} as target")
    else:
        await update.message.reply_text("✅ This chat has been set as your target for video downloads.")
        logger.info(f"User {user_id} in chat {chat_id} set chat {chat_id} as target")

async def clear_topic_channel(update: Update, context) -> None:
    """Clear the target topic/channel setting."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    user_prefs = get_user_prefs(chat_id, user_id)
    
    if 'target_chat_id' in user_prefs:
        del user_prefs['target_chat_id']
    if 'target_topic_id' in user_prefs:
        del user_prefs['target_topic_id']
    
    await update.message.reply_text("❌ Target topic/chat has been cleared. Videos will now be sent to the chat where links are shared.")
    logger.info(f"User {user_id} in chat {chat_id} cleared target chat/topic setting")

async def download(update: Update, context) -> None:
    """Gets video URLs from a telegram message, downloads the videos, and sends messages with them."""
    try:
        await update.message.set_reaction(reaction=ReactionTypeEmoji("👀"))
        urls = re.findall(r"(https?://\S+)", update.message.text)
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Get user preferences for this specific chat
        user_prefs = get_user_prefs(chat_id, user_id)
        
        # Check if the user wants descriptions in this chat
        show_description = user_prefs.get('show_description', False)
        
        # Check if the user has a designated target chat/topic for this chat
        target_chat_id = user_prefs.get('target_chat_id', None)
        target_topic_id = user_prefs.get('target_topic_id', None)
        
        # Use original chat if no target is set
        if target_chat_id is None:
            target_chat_id = update.effective_chat.id
            target_topic_id = update.effective_message.message_thread_id if hasattr(update.effective_message, 'message_thread_id') else None
        
        success_count = 0
        failure_count = 0
            
        for url in urls:
            logger.info(f"Processing URL: {url}")
            try:
                await update.message.set_reaction(reaction=ReactionTypeEmoji("⚡"))
                
                if show_description:
                    # With descriptions enabled, include video info
                    file_path, video_info = download_reel(url, get_description=True)
                    
                    # Create a caption with video information
                    caption = format_video_caption(update, video_info)
                else:
                    # Without descriptions, just download the video
                    file_path = download_reel(url)
                    caption = from_user(update)
                
                # Send to the target chat/topic
                await context.bot.send_video(
                    chat_id=target_chat_id,
                    message_thread_id=target_topic_id,
                    video=open(file_path, 'rb'),
                    caption=caption,
                    disable_notification=True,
                    read_timeout=600,
                    write_timeout=600,
                    connect_timeout=600,
                    pool_timeout=600,
                )
                
                os.remove(file_path)
                success_count += 1
            except Exception as e:
                failure_count += 1
                logger.error(f"Error processing URL {url}: {str(e)}")
                
                # More specific error message - send to the original chat not the target
                error_msg = str(e)
                if "unsupported URL" in error_msg.lower():
                    await update.message.reply_text(f"❌ Unsupported URL format: {url}")
                elif "copyright" in error_msg.lower():
                    await update.message.reply_text(f"❌ Content unavailable due to copyright: {url}")
                else:
                    await update.message.reply_text(f"❌ Failed to process URL: {url}\nError: {error_msg[:100]}...")
                
                with open('failed_links.log', 'a') as f:
                    f.write(f"{url} - Error: {str(e)}\n")
        
        
        # Delete the original message with links
        await update.effective_message.delete()
    except Exception as e:
        await update.message.set_reaction(reaction=ReactionTypeEmoji("👎"))
        logger.error(f"General error: {str(e)}")
        logger.error(traceback.format_exc())
        
        with open('failed_links.log', 'a') as f:
            f.write(f"{update.message.text} - General error: {str(e)}\n")

def format_video_caption(update, video_info):
    """Format video information into a caption."""
    # Start with the user info
    caption = from_user(update) + "\n\n"
    
    # Add video information
    caption += f"📹 *{video_info.get('title', 'No title')}*\n"
    
    # Add uploader if available
    if video_info.get('uploader') and video_info.get('uploader') != 'Unknown uploader':
        caption += f"👤 {video_info.get('uploader')}\n"
    
    # Format the date if available
    upload_date = video_info.get('upload_date')
    if upload_date and upload_date != 'Unknown date':
        try:
            formatted_date = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[0:4]}"
            caption += f"📅 {formatted_date}\n"
        except:
            pass
    
    # Add view count if available
    if video_info.get('view_count') and video_info.get('view_count') != 'Unknown views':
        caption += f"👁 {video_info.get('view_count')} views\n"
    
    # Add description (truncated if too long)
    description = video_info.get('description', '')
    if description and description != 'No description available':
        # Truncate if needed to stay within Telegram's limits
        max_desc_len = 800  # Leave room for other caption content
        if len(description) > max_desc_len:
            description = description[:max_desc_len] + "..."
        
        caption += f"{description}"
    
    # Ensure we don't exceed Telegram's caption limit (1024 characters)
    if len(caption) > 1024:
        caption = caption[:1021] + "..."
        
    return caption

def from_user(update):
    """Returns a formatted string with the username or first name of the user."""
    if update.effective_user.username:
        return f"From @{update.effective_user.username}"
    else:
        return f"From {update.effective_user.first_name}"

async def start(update: Update, context) -> None:
    """Send a welcome message when the command /start is issued."""
    welcome_message = (
        "👋 Hello! I can download videos from various platforms.\n\n"
        "Just send me a message containing a link to a video from: "
        "9GAG, Twitter/X, Instagram Reels, TikTok, Facebook Reels, or YouTube Shorts."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context) -> None:
    """Send a help message when the command /help is issued."""
    help_text = (
        "📋 *Commands*:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/report - Generate a report of failed downloads\n"
        "/toggledesc - Toggle video descriptions on/off\n"
        "/settopic - Set current chat/topic as target for downloads\n"
        "/cleartopic - Clear target chat/topic setting\n\n"
        "📱 *Supported Platforms*:\n"
        "• 9GAG\n"
        "• Twitter/X\n"
        "• Instagram Reels\n"
        "• TikTok\n"
        "• Facebook Reels\n"
        "• YouTube Shorts"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def test_func(update: Update, context) -> None:
    """Sets a banana reaction to the message."""
    await update.message.set_reaction(reaction=ReactionTypeEmoji("🍌"))

async def create_failed_link_report(update: Update, context) -> None:
    """Sends the content of failed_links.log to the user and clears the file."""
    try:
        with open('failed_links.log', 'r') as f:
            failed_links = f.read()
        
        if not failed_links:
            await update.message.reply_text("No failed links recorded.")
            return
            
        # If the report is too long, split it or send as a file
        if len(failed_links) > 4000:
            with open('report.txt', 'w') as f:
                f.write(failed_links)
            await update.message.reply_document(
                document=open('report.txt', 'rb'),
                filename='failed_links_report.txt',
                caption="Report of failed downloads"
            )
            os.remove('report.txt')
        else:
            await update.message.reply_text(failed_links)
            
        # Clear the file after reporting
        open('failed_links.log', 'w').close()
        logger.info("Failed links report generated and file cleared")
    except FileNotFoundError:
        await update.message.reply_text("No failed links recorded.")

def main():
    """Start the bot."""
    # Create the Application and pass the bot's token
    app = ApplicationBuilder().token(os.environ.get("BOT_API_KEY")).build()
    
    # Define regex patterns for each platform
    url_patterns = {
        "9gag": r".*9gag\.com\/gag\/.*",
        "twitter": r".*x\.com\/.*\/status\/.*",
        "instagram": r".*www.instagram\.com\/.*reel.*",
        "tiktok": r".*.tiktok.com\/.*",
        "facebook": r"(.*www\.facebook\.com\/reel.*)|(.*fb\.watch\/.*)|(.*www\.facebook\.com\/share.*)",
        "youtube": r".*(www\.|)youtube\.com\/shorts\/.*"
    }
    
    # Combined pattern
    combined_pattern = "|".join(f"({pattern})" for pattern in url_patterns.values())
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("report", create_failed_link_report))
    
    # Add handlers for preferences (as commands now)
    app.add_handler(CommandHandler("toggledesc", toggle_description))
    app.add_handler(CommandHandler("settopic", set_topic_channel))
    app.add_handler(CommandHandler("cleartopic", clear_topic_channel))
    
    # Keep old message handlers for backward compatibility
    app.add_handler(MessageHandler(filters.Regex(r"^optInDescription$"), toggle_description))
    app.add_handler(MessageHandler(filters.Regex(r"^initCurrentTopicAsMemeBotTopic$"), set_topic_channel))
    app.add_handler(MessageHandler(filters.Regex(r"^clearMemeBotTopic$"), clear_topic_channel))
    
    app.add_handler(MessageHandler(filters.Regex(combined_pattern), download))
    app.add_handler(MessageHandler(filters.Regex(r".*banana*."), test_func))
    
    # Start the Bot
    logger.info("Bot started")
    app.run_polling()

if __name__ == '__main__':
    main()

