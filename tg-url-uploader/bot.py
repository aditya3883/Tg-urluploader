import os
import time
import json
import signal
import subprocess
import threading

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from web import app as web_app

# ---------- ENV ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

JOB_FILE = "jobs.json"

current_process = None
cancel_flag = False
txt_path = None


# ---------- KEEP ALIVE WEB ----------
def run_web():
    web_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()
