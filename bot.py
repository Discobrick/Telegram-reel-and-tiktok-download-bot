"""
Telegram bot for downloading videos from various platforms.

This module provides a Telegram bot that can download videos from platforms
like 9GAG, Twitter/X, Instagram Reels, TikTok, Facebook Reels, and YouTube Shorts.
"""
import json
import logging as log
import os
import re
import traceback
import asyncio
import concurrent.futures
from telegram import Update
from telegram import ReactionTypeEmoji
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler

from scraper import download_reel

# File path for persistent preferences - using /data for the named Docker volume
PREFERENCES_FILE = os.environ.get('PREFERENCES_FILE', '/data/preferences.json')
DATA_DIR = os.path.dirname(PREFERENCES_FILE)

# Create a fallback directory for logs if DATA_DIR isn't writable
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    # Test if the directory is writable by creating a temporary file
    test_file = os.path.join(DATA_DIR, '.write_test')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    # DATA_DIR is writable, use it
    LOG_DIR = DATA_DIR
except (IOError, PermissionError):
    # DATA_DIR not writable, use a local directory instead
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"Warning: Cannot write to {DATA_DIR}, using {LOG_DIR} instead")

# Log files paths
ERROR_LOG_FILE = os.environ.get('ERROR_LOG_FILE', os.path.join(LOG_DIR, 'error.log'))
FAILED_LINKS_LOG_FILE = os.environ.get('FAILED_LINKS_LOG_FILE', os.path.join(LOG_DIR, 'failed_links.log'))

# Configure logging to file and console
log.basicConfig(
    level=log.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        log.FileHandler(ERROR_LOG_FILE),
        log.StreamHandler()
    ]
)

logger = log.getLogger(__name__)

# Store preferences by chat_id and user_id
# Format: preferences[chat_id][user_id] = {'show_description': bool, 'target_chat_id': int, ...}
preferences = {}

# Thread pool executor for parallel downloads
# We'll limit the number of concurrent downloads to avoid overwhelming the system
MAX_WORKERS = os.environ.get('MAX_WORKERS', 5)
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=int(MAX_WORKERS))

def load_preferences():
    """Load preferences from file if it exists."""
    global preferences
    try:
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                # JSON can't use integers as keys, so they're stored as strings
                # We need to convert them back to integers
                string_prefs = json.load(f)
                preferences = {
                    int(chat_id): {
                        int(user_id): prefs 
                        for user_id, prefs in chat_prefs.items()
                    }
                    for chat_id, chat_prefs in string_prefs.items()
                }
            logger.info("Preferences loaded from %s", PREFERENCES_FILE)
        else:
            logger.info("No preferences file found at %s, using empty preferences", PREFERENCES_FILE)
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
            # Initialize empty preferences file
            save_preferences()
    except Exception as e:
        logger.error("Failed to load preferences: %s", str(e))
        # Continue with empty preferences if loading fails

def save_preferences():
    """Save preferences to file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
        
        # Convert integer keys to strings for JSON serialization
        string_prefs = {
            str(chat_id): {
                str(user_id): prefs 
                for user_id, prefs in chat_prefs.items()
            }
            for chat_id, chat_prefs in preferences.items()
        }
        
        with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(string_prefs, f, indent=2)
        
        logger.info("Preferences saved to %s", PREFERENCES_FILE)
    except Exception as e:
        logger.error("Failed to save preferences: %s", str(e))

def get_user_prefs(chat_id, user_id):
    """Get user preferences for a specific chat."""
    if chat_id not in preferences:
        preferences[chat_id] = {}

    if user_id not in preferences[chat_id]:
        preferences[chat_id][user_id] = {}

    return preferences[chat_id][user_id]

async def toggle_description(update: Update, _context) -> None:
    """Toggle showing descriptions for videos."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    user_prefs = get_user_prefs(chat_id, user_id)

    # Toggle the preference
    current_preference = user_prefs.get('show_description', False)
    user_prefs['show_description'] = not current_preference

    # Save preferences to persistent storage
    save_preferences()

    # Confirm to the user
    status = "enabled" if user_prefs['show_description'] else "disabled"
    await update.message.reply_text(f"Video descriptions are now {status} for your downloads in this chat.")
    logger.info("User %s in chat %s set description preference to %s", user_id, chat_id, status)

async def set_topic_channel(update: Update, _context) -> None:
    """Set current topic/channel as target for video downloads."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message_thread_id = update.effective_message.message_thread_id if hasattr(update.effective_message, 'message_thread_id') else None

    user_prefs = get_user_prefs(chat_id, user_id)

    # Save the target channel/topic information
    user_prefs['target_chat_id'] = chat_id
    user_prefs['target_topic_id'] = message_thread_id

    # Save preferences to persistent storage
    save_preferences()

    # Create confirmation message based on whether it's a topic or just a chat
    if message_thread_id:
        await update.message.reply_text("✅ This topic has been set as your target for video downloads.")
        logger.info("User %s in chat %s set topic %s as target", user_id, chat_id, message_thread_id)
    else:
        await update.message.reply_text("✅ This chat has been set as your target for video downloads.")
        logger.info("User %s in chat %s set chat %s as target", user_id, chat_id, chat_id)

async def clear_topic_channel(update: Update, _context) -> None:
    """Clear the target topic/channel setting."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    user_prefs = get_user_prefs(chat_id, user_id)

    if 'target_chat_id' in user_prefs:
        del user_prefs['target_chat_id']
    if 'target_topic_id' in user_prefs:
        del user_prefs['target_topic_id']

    # Save preferences to persistent storage
    save_preferences()

    await update.message.reply_text("❌ Target topic/chat has been cleared. Videos will now be sent to the chat where links are shared.")
    logger.info("User %s in chat %s cleared target chat/topic setting", user_id, chat_id)

def process_single_url(url, update, context, show_description, target_chat_id, target_topic_id):
    """Process a single URL for download and sending to the user.
    
    This function runs in a separate thread for each URL and returns the result.
    """
    try:
        logger.info("Processing URL: %s", url)
        
        if show_description:
            # With descriptions enabled, include video info
            file_path, video_info = download_reel(url, get_description=True)
            
            # Create a caption with video information
            full_caption = format_video_caption(update, video_info)
            
            # Check if caption exceeds Telegram's limit
            if len(full_caption) > 1024:
                # For the video, use a truncated caption
                caption = full_caption[:1021] + "..."
                
                # Prepare additional messages for the rest of the caption
                remaining_text = full_caption[1021:]
                
                # Split remaining text into chunks of 1024 characters (Telegram message limit)
                text_chunks = []
                while remaining_text:
                    if len(remaining_text) <= 1024:
                        text_chunks.append(remaining_text)
                        remaining_text = ""
                    else:
                        text_chunks.append(remaining_text[:1021] + "...")
                        remaining_text = remaining_text[1021:]
            else:
                caption = full_caption
                text_chunks = []
        else:
            # Without descriptions, just download the video
            file_path = download_reel(url)
            caption = from_user(update)
            text_chunks = []
        
        return True, None, url, file_path, caption, text_chunks
    except Exception as e:
        error_msg = str(e)
        logger.error("Error processing URL %s: %s", url, error_msg)
        
        # Log the failed URL
        os.makedirs(os.path.dirname(FAILED_LINKS_LOG_FILE), exist_ok=True)
        with open(FAILED_LINKS_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{url} - Error: {str(e)}\n")
            
        return False, error_msg, url, None, None, None

async def download_url_in_thread(url, update, context, show_description, target_chat_id, target_topic_id):
    """Run the URL download process in a separate thread.
    
    This function wraps process_single_url to be run in a thread pool executor,
    enabling parallel downloads.
    """
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        logger.info("Starting new download thread for URL: %s (User: %s, Chat: %s)", url, user_id, chat_id)
        
        # Use run_in_executor to run the CPU-bound download operation in a separate thread
        return await asyncio.get_event_loop().run_in_executor(
            thread_pool,
            lambda: process_single_url(url, update, context, show_description, target_chat_id, target_topic_id)
        )
    except Exception as e:
        logger.error("Error in download thread for URL %s: %s", url, str(e))
        return False, str(e), url

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
        
        # Use asyncio.gather with run_in_executor to run downloads in parallel
        tasks = []
        for url in urls:
            # Create a task for each URL to download and process
            task = asyncio.create_task(
                download_url_in_thread(url, update, context, show_description, target_chat_id, target_topic_id)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Process results
        for success, error_msg, url, file_path, caption, text_chunks in results:
            if success:
                # Send the video with the caption
                try:
                    with open(file_path, 'rb') as video_file:
                        sent_message = await context.bot.send_video(
                            chat_id=target_chat_id,
                            message_thread_id=target_topic_id,
                            video=video_file,
                            caption=caption,
                            disable_notification=True,
                            read_timeout=600,
                            write_timeout=600,
                            connect_timeout=600,
                            pool_timeout=600,
                        )
                    
                    # Send additional messages with the rest of the caption if needed
                    for chunk in text_chunks:
                        await context.bot.send_message(
                            chat_id=target_chat_id,
                            message_thread_id=target_topic_id,
                            text=chunk,
                            disable_notification=True,
                            reply_to_message_id=sent_message.message_id
                        )
                    
                    # Clean up the file
                    os.remove(file_path)
                    success_count += 1
                    await update.message.set_reaction(reaction=ReactionTypeEmoji("⚡"))
                    await update.effective_message.delete()
                except Exception as e:
                    failure_count += 1
                    logger.error("Error sending video for URL %s: %s", url, str(e))
                    await update.message.reply_text(f"❌ Failed to send video: {url}\nError: {str(e)[:100]}...")
            else:
                failure_count += 1
                # More specific error message - send to the original chat not the target
                if "unsupported URL" in error_msg.lower():
                    logger.error(f"❌ Unsupported URL format: {url}")
                    logger.error(traceback.format_exc())
                    await update.message.set_reaction(reaction=ReactionTypeEmoji("🖕"))
                elif "copyright" in error_msg.lower():
                    logger.error(f"❌ Content unavailable due to copyright: {url}")
                    logger.error(traceback.format_exc())
                    await update.message.set_reaction(reaction=ReactionTypeEmoji("🖕"))
                else:
                    logger.error(f"❌ Failed to process URL: {url}\nError: {error_msg[:100]}...")
                    logger.error(traceback.format_exc())
                    await update.message.set_reaction(reaction=ReactionTypeEmoji("🖕"))

    except Exception as e:
        await update.message.set_reaction(reaction=ReactionTypeEmoji("👎"))
        logger.error("General error: %s", str(e))
        logger.error(traceback.format_exc())
        
        # Ensure directory for failed links log exists
        os.makedirs(os.path.dirname(FAILED_LINKS_LOG_FILE), exist_ok=True)
        with open(FAILED_LINKS_LOG_FILE, 'a', encoding='utf-8') as f:
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
        except IndexError:
            pass
    
    # Add view count if available
    if video_info.get('view_count') and video_info.get('view_count') != 'Unknown views':
        caption += f"👁 {video_info.get('view_count')} views\n"
    
    # Add description without truncating
    description = video_info.get('description', '')
    if description and description != 'No description available':
        caption += f"{description}"
    
    return caption

def from_user(update):
    """Returns a formatted string with the username or first name of the user."""
    user = update.effective_user
    if user.username:
        return f"From @{user.username}"
    elif user.first_name:
        return f"From {user.first_name}"
    else:
        return "From an unknown user"


async def start(update: Update, _context) -> None:
    """Send a welcome message when the command /start is issued."""
    welcome_message = (
        "👋 Hello! I can download videos from various platforms.\n\n"
        "Just send me a message containing a link to a video from: "
        "9GAG, Twitter/X, Instagram Reels, TikTok, Facebook Reels, or YouTube Shorts."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, _context) -> None:
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

async def test_func(update: Update, _context) -> None:
    """Sets a banana reaction to the message."""
    await update.message.set_reaction(reaction=ReactionTypeEmoji("🍌"))

async def create_failed_link_report(update: Update, _context) -> None:
    """Sends the content of failed_links.log to the user and clears the file."""
    try:
        # Check if failed links file exists
        if not os.path.exists(FAILED_LINKS_LOG_FILE):
            await update.message.reply_text("No failed links recorded.")
            return
            
        with open(FAILED_LINKS_LOG_FILE, 'r', encoding='utf-8') as f:
            failed_links = f.read()

        if not failed_links:
            await update.message.reply_text("No failed links recorded.")
            return

        # If the report is too long, split it or send as a file
        if len(failed_links) > 4000:
            # Create the temporary report file in the same persistent directory
            temp_report_file = os.path.join(DATA_DIR, 'report.txt')
            
            with open(temp_report_file, 'w', encoding='utf-8') as f:
                f.write(failed_links)

            with open(temp_report_file, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename='failed_links_report.txt',
                    caption="Report of failed downloads"
                )
            
            # Clean up temporary file
            try:
                os.remove(temp_report_file)
            except Exception as e:
                logger.warning("Could not remove temporary report file: %s", str(e))
        else:
            await update.message.reply_text(failed_links)

        # Clear the file after reporting
        try:
            with open(FAILED_LINKS_LOG_FILE, 'w', encoding='utf-8') as f:
                pass
            logger.info("Failed links report generated and file cleared")
        except Exception as e:
            logger.error("Could not clear failed links file: %s", str(e))
            await update.message.reply_text("Note: Could not clear failed links log.")
            
    except FileNotFoundError:
        await update.message.reply_text("No failed links recorded.")
    except Exception as e:
        logger.error("Error generating report: %s", str(e))
        await update.message.reply_text(f"Error generating report: {str(e)}")

def main():
    """Start the bot."""
    # Load preferences from persistent storage
    load_preferences()

    # Create the Application and pass the bot's token
    app = ApplicationBuilder().token(os.environ.get("BOT_API_KEY")).build()

    # Define regex patterns for each platform
    url_patterns = {
        "9gag": r".*9gag\.com\/gag\/.*",
        "twitter": r".*x\.com\/.*\/status\/.*",
        "instagram": r".*www.instagram\.com\/.*reel.*",
        "tiktok": r".*.tiktok.com\/.*",
        "facebook": (r"(.*www\.facebook\.com\/reel.*)|"
                    r"(.*fb\.watch\/.*)|"
                    r"(.*www\.facebook\.com\/share.*)"),
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
    app.add_handler(MessageHandler(
        filters.Regex(r"^initCurrentTopicAsMemeBotTopic$"),
        set_topic_channel
    ))
    app.add_handler(MessageHandler(filters.Regex(r"^clearMemeBotTopic$"), clear_topic_channel))

    app.add_handler(MessageHandler(filters.Regex(combined_pattern), download))
    app.add_handler(MessageHandler(filters.Regex(r".*banana*."), test_func))

    # Start the Bot
    logger.info("Bot started")
    app.run_polling()

if __name__ == '__main__':
    main()