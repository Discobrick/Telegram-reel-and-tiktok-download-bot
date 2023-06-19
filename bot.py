import glob
import logging as log
import os

from telegram import Update
from telegram.ext import (ApplicationBuilder, ContextTypes, MessageHandler,
                          filters)

from reelScrape import downloadReel

downloadDir = os.path.dirname(os.path.realpath(__file__))+ "\downloads"

botToken = "BOT-API-TOKEN"

def getFilePath():
    for filename in glob.glob(downloadDir + '\*.mp4'):
        return filename

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    downloadReel(update.message.text)
    try:
        await update.message.reply_video(getFilePath(),quote=False,disable_notification=True,read_timeout=180,write_timeout=180,connect_timeout=180,pool_timeout=180)
        await update.effective_message.delete()
    except Exception:
        log.error('Error for link: ' + update.message.text)
    finally:
        os.remove(getFilePath())

app = ApplicationBuilder().token(botToken).build()
app.add_handler(MessageHandler(filters.Regex(r"(.*www.instagram\.com\/reel.*)|(.*vm.tiktok.com\/)|(.*www.facebook\.com\/reel.*)"), download))
app.run_polling()

