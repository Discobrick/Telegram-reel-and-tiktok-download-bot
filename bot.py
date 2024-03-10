import logging as log
import os

from telegram import Update
from telegram import ReactionType,ReactionTypeEmoji
from telegram.ext import (ApplicationBuilder, MessageHandler,filters)

from reel_scrape import download_reel

global meme_bot_init,meme_bot_topic

meme_bot_init = False
meme_bot_topic = ""

async def download(update: Update,context) -> None:
    """Gets video url from a telegram message, downloads the video, and sends a message with it."""
    try:
        await update.message.set_reaction(reaction=ReactionTypeEmoji("👀"))
        filePath = download_reel(update.message.text,update.effective_user.username)
        if meme_bot_init == True and update.effective_chat.is_forum:
            await update.message.set_reaction(reaction=ReactionTypeEmoji("⚡"))
            await update.message.reply_video(filePath,caption='From @'+update.effective_user.username,quote=False,disable_notification=True,read_timeout=300,write_timeout=300,connect_timeout=300,pool_timeout=300,message_thread_id=meme_bot_topic)
        else:
            await update.message.set_reaction(reaction=ReactionTypeEmoji("⚡"))
            await update.message.reply_video(filePath,caption='From @'+update.effective_user.username,quote=False,disable_notification=True,read_timeout=300,write_timeout=300,connect_timeout=300,pool_timeout=300)
        await update.effective_message.delete()
        os.remove(filePath)
    except Exception as e:
        await update.message.set_reaction(reaction=ReactionTypeEmoji("👎"))
        log.error('Error for link: ' + update.message.text)  
        log.error(e)

async def initMemeTopic(update: Update, context) -> None:
    global meme_bot_init,meme_bot_topic
    if meme_bot_init is False:
        meme_bot_topic = str(update.effective_message.reply_to_message.message_thread_id)
        meme_bot_init = True
        await update.effective_message.delete()

async def resetMemeTopic(update: Update, context) -> None:
    global meme_bot_init,meme_bot_topic
    if meme_bot_topic == str(update.effective_message.reply_to_message.message_thread_id):
        meme_bot_init = False
        meme_bot_topic = ""
        await update.effective_message.delete()

async def testFunc(update: Update, context) -> None:
    await update.message.set_reaction(reaction=ReactionTypeEmoji("🍌"))
    await update.message.reply_text("test test")

app = ApplicationBuilder().token(os.environ.get('BOT_API_KEY')).build()


app.add_handler(MessageHandler(filters.Regex(r"(.*www.instagram\.com\/reel.*)|(.*.tiktok.com\/)|(.*www\.facebook\.com\/reel.*)|(.*fb\.watch\/.*)|(.*www\.facebook\.com\/share.*)|(.*(www\.|)youtube\.com\/shorts\/.*)"), download))
app.add_handler(MessageHandler(filters.Regex(r"initCurrentTopicAsMemeBotTopic"),initMemeTopic))
app.add_handler(MessageHandler(filters.Regex(r"resetMemeTopic"),resetMemeTopic))
app.run_polling()
