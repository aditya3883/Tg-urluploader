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
print("BOT_TOKEN loaded:", bool(BOT_TOKEN))
print("ADMIN_ID loaded:", ADMIN_ID)

# ---------- KEEP ALIVE WEB ----------
def run_web():
    web_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# ---------- JOB FILE HELPERS ----------
def save_job(data):
    with open(JOB_FILE, "w") as f:
        json.dump(data, f)

def load_job():
    if not os.path.exists(JOB_FILE):
        return None
    with open(JOB_FILE) as f:
        return json.load(f)

def clear_job():
    if os.path.exists(JOB_FILE):
        os.remove(JOB_FILE)


# ---------- TXT PARSER ----------
def read_links(file_path):
    data = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                name, url = line.strip().split("|", 1)
                data.append((name.strip(), url.strip()))
    return data


# ---------- /start COMMAND ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "🚀 *Advanced URL Uploader Bot*\n\n"
        "📄 Send a `.txt` file in this format:\n"
        "`Video Name | Video URL`\n\n"
        "▶️ After uploading txt, use /run\n"
        "❌ Use /cancel to stop",
        parse_mode="Markdown"
    )


# ---------- TXT FILE HANDLER ----------
async def txt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global txt_path

    if update.effective_user.id != ADMIN_ID:
        return

    document = update.message.document

    if not document.file_name.endswith(".txt"):
        await update.message.reply_text("❌ Only .txt files are allowed")
        return

    tg_file = await document.get_file()
    txt_path = f"input_{int(time.time())}.txt"
    await tg_file.download_to_drive(txt_path)

    items = read_links(txt_path)

    await update.message.reply_text(
        f"✅ TXT file received successfully\n"
        f"📂 Total links found: {len(items)}"
    )


# ---------- BOT INITIALIZATION ----------
application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.ALL, txt_handler))

print("🤖 Bot polling started...")
application.run_polling(close_loop=False)
