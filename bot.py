import glob
import logging as log
import os

from telegram import Update
from telegram.ext import (ApplicationBuilder, ContextTypes, MessageHandler,
                          filters)

from reelScrape import downloadReel

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    filePath = downloadReel(update.message.text,update.effective_user.username)
    try:
        await update.message.reply_video(filePath,caption='From @'+update.effective_user.username,quote=False,disable_notification=True,read_timeout=180,write_timeout=180,connect_timeout=180,pool_timeout=180)
        await update.effective_message.delete()
    except Exception:
        await update.message.reply_text(text="Can't download this",quote=True)
        log.error('Error for link: ' + update.message.text)
    finally:
        os.remove(filePath)

app = ApplicationBuilder().token(os.environ.get('BOT_API_KEY')).build()


app.add_handler(MessageHandler(filters.Regex(r"(.*www.instagram\.com\/reel.*)|(.*.tiktok.com\/)|(.*www.facebook\.com\/reel.*)|(.*fb.watch\/.*)|(.*9gag\.com\/gag\/.*)"), download))


app.run_polling()