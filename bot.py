import logging as log
import os

from telegram import Update
from telegram.ext import (ApplicationBuilder, MessageHandler,filters)

from reel_scrape import download_reel

global meme_bot_init,meme_bot_topic

meme_bot_init = False
meme_bot_topic = ""

async def download(update: Update,context) -> None:
    """Gets video url from a telegram message, downloads the video, and sends a message with it."""
    try:
        filePath = download_reel(update.message.text,update.effective_user.username)
        if meme_bot_init == True and update.effective_chat.is_forum:
            await update.message.reply_video(filePath,caption='From @'+update.effective_user.username,quote=False,disable_notification=True,read_timeout=180,write_timeout=180,connect_timeout=180,pool_timeout=180,message_thread_id=meme_bot_topic)
        else:
            await update.message.reply_video(filePath,caption='From @'+update.effective_user.username,quote=False,disable_notification=True,read_timeout=180,write_timeout=180,connect_timeout=180,pool_timeout=180)
        await update.effective_message.delete()
        os.remove(filePath)
    except Exception as e:
        await update.message.reply_text(text="Can't download",quote=True)
        log.error('Error for link: ' + update.message.text)  
        log.error(e)

async def initMemeTopic(update: Update, context) -> None:
    global meme_bot_init,meme_bot_topic
    if meme_bot_init is False:
        meme_bot_topic = str(update.effective_message.reply_to_message.message_thread_id)
        meme_bot_init = True

async def resetMemeTopic(update: Update, context) -> None:
    global meme_bot_init,meme_bot_topic
    if meme_bot_topic == str(update.effective_message.reply_to_message.message_thread_id):
        meme_bot_init = False
        meme_bot_topic = ""


app = ApplicationBuilder().token(os.environ.get('BOT_API_KEY')).build()


app.add_handler(MessageHandler(filters.Regex(r"(.*www.instagram\.com\/reel.*)|(.*.tiktok.com\/)|(.*www.facebook\.com\/reel.*)|(.*fb.watch\/.*)|(.*9gag\.com\/gag\/.*)"), download))
app.add_handler(MessageHandler(filters.Regex(r"initCurrentTopicAsMemeBotTopic"),initMemeTopic))
app.add_handler(MessageHandler(filters.Regex(r"resetMemeTopic"),resetMemeTopic))

app.run_polling()