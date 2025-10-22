# main.py
import os
import random
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, InlineQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== 200 Persian questions (short version here, add full 200) =====
QUESTIONS = [
    "1. اولین خاطره کودکی‌ات چیه؟",
    "2. چه غذایی رو همیشه دوست داشتی ولی الآن ازش بیزاری؟",
    "3. یه عادتی که مردم ازت تعجب می‌کنن چیه؟",
    "4. مهم‌ترین دغدغه‌ات این روزها چیه؟",
    # ... add all 200 questions here
]

def pick_question():
    return random.choice(QUESTIONS)

# ===== Flask server for Render Web Service =====
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

# Run Flask in a separate thread so the bot can start too
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ===== Telegram Bot Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = [[InlineKeyboardButton("سوال میخوام", callback_data="new_question")]]
    reply_markup = InlineKeyboardMarkup(button)
    await update.message.reply_text("سلام! دکمه رو بزن تا یه سوال تصادفی بگیرید.", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    question = pick_question()
    button = [[InlineKeyboardButton("یه سوال دیگه", callback_data="new_question")]]
    reply_markup = InlineKeyboardMarkup(button)
    await query.edit_message_text(question, reply_markup=reply_markup)

async def question_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(pick_question())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "سوال" in (update.message.text or ""):
        await update.message.reply_text(pick_question())
    else:
        await update.message.reply_text("برای گرفتن سوال دکمهٔ «سوال میخوام» یا /question رو امتحان کن.")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query
    question = pick_question()
    result = InlineQueryResultArticle(
        id=str(random.getrandbits(64)),
        title="سوال تصادفی",
        input_message_content=InputTextMessageContent(question),
        description=question[:50] + ("..." if len(question) > 50 else "")
    )
    await query.answer([result], cache_time=0)

# ===== Main =====
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Please set TELEGRAM_BOT_TOKEN environment variable")

    keep_alive()  # start Flask server so Render sees the port

    bot_app = ApplicationBuilder().token(token).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("question", question_cmd))
    bot_app.add_handler(CallbackQueryHandler(handle_button))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    bot_app.add_handler(InlineQueryHandler(inline_query))

    logger.info("Bot is running...")
    bot_app.run_polling()

if __name__ == "__main__":
    main()
