# main.py
import os
import random
import logging
from threading import Thread
from flask import Flask
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, InlineQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== 200 Persian questions (shortened here; add all 200) =====
QUESTIONS = [
"1. اولین خاطره کودکی‌ات چیه؟",
"2. چه غذایی رو همیشه دوست داشتی ولی الآن ازش بیزاری؟",
"3. یه عادتی که مردم ازت تعجب می‌کنن چیه؟",
"4. مهم‌ترین دغدغه‌ات این روزها چیه؟",
"5. از کدوم فیلم یا سریال همیشه خوش‌ت میاد؟",
"6. بهترین هدیه‌ای که گرفتی چی بود؟",
"7. یه چیزی که همیشه با خودت می‌بری کجای دستته؟",
"8. اگه بتونی یه استعداد فوق‌العاده بگیری، چی انتخاب می‌کنی؟",
"9. یه ترس خنده‌دار یا عجیب که داشتی چیه؟",
"10. صبح‌ها چطور بیدار می‌شی؟ حساس یا راحت؟",
"11. یه موسیقی که همیشه حالت رو بهتر می‌کنه؟",
"12. اگر یه روز کامل رو می‌تونستی تغییر بدی، چه کاری می‌کردی؟",
"13. تا حالا چیزی گفتی که بعد پشیمون شدی؟",
"14. وقتی عصبانی می‌شی، چه کار می‌کنی؟",
"15. بهترین چیزی که توی یک تعطیلات انجام دادی چی بود؟",
"16. یه خاطره خنده‌دار از مدرسه تعریف کن",
"17. از چه چیزی بیش‌تر از همه می‌ترسی؟",
"18. تا حالا کسی برات سوپرایز انجام داده؟",
"19. اگر یک روز همه چیز بر وفق مرادت باشه، چه اتفاقی می‌افته؟",
"20. یه عادت عجیب داری که مردم ازش تعجب می‌کنن؟",
"21. وقتی تنها هستی، چه کار می‌کنی؟",
"22. یه مهارت داری که بقیه نمی‌دونن؟",
"23. اگر بخوای یه روز رو دوباره زندگی کنی، چه چیزی رو تغییر می‌دادی؟",
"24. بهترین جوکی که شنیدی چی بود؟",
"25. آیا تا حالا چیزی رو پنهان کردی ولی الان دلت می‌خواد بگی؟",
"26. یک لحظه خجالت‌آور که هنوز یادت می‌آد چی بود؟",
"27. اگر پول بی‌نهایت داشتی، اولین کاری که می‌کردی چی بود؟",
"28. اهل ورزش هستی؟ کدوم ورزش؟",
"29. چه غذایی باعث می‌شه یاد یه خاطره بیفتی؟",
"30. دوست داری بیشتر تنها باشی یا با جمع؟",
"31. یه چیزی که همیشه می‌خوای یاد بگیری چیه؟",
"32. اگر بخوای یه سفر کوتاه بکنی، کجا می‌ری؟",
"33. چه چیزی تو رو سریع خوشحال می‌کنه؟",
"34. بهترین لحظه خنده‌دار که تا حالا داشتی چی بود؟",
"35. چیزی که باعث می‌شه احساس امنیت کنی چیه؟",
"36. اولین کسی که بهش علاقه‌مند شدی کی بود؟",
"37. اولین باری که قلبت تند زد کی بود؟",
"38. چه چیزی باعث شد اولین رابطه‌ت رو فراموش نکنی؟",
"39. وقتی کسی دوستت داشته باشه، چه احساسی داری؟",
"40. بهترین لحظه‌ای که با کسی گذروندی چی بود؟",
"41. تا حالا کسی باعث شد حس حسادت کنی؟",
"42. یه عادتی که بقیه نمی‌فهمن ولی تو داری چی هست؟",
"43. وقتی ناراحت هستی، چه کار می‌کنی تا آروم بشی؟",
"44. چه چیزی باعث می‌شه از یک روز معمولی لذت ببری؟",
"45. یه اتفاق عجیب یا غیرمنتظره که برات پیش اومده تعریف کن",
"46. آیا تا حالا راز کسی رو نگه داشتی؟",
"47. اگر بتونی یه مهارت عجیب یاد بگیری، چی انتخاب می‌کنی؟",
"48. یه خاطره خنده‌دار از سفر تعریف کن",
"49. وقتی می‌خوای تصمیم مهم بگیری، چه کاری انجام می‌دی؟",
"50. بهترین چیزی که اخیراً یاد گرفتی چی بود؟",
"51. یک عادتی که تو رو خوشحال می‌کنه چیه؟",
"52. تا حالا چیزی گفتی که باعث خنده دیگران شد؟",
"53. بهترین راه برای شروع روزت چیه؟",
"54. وقتی یه روز بد داری، چه کار می‌کنی؟",
"55. دوست داری روزت با چه کسی بگذرونی؟",
"56. چه چیزی باعث می‌شه حس کنی موفق هستی؟",
"57. تا حالا یه اشتباه خنده‌دار کردی؟",
"58. یه خاطره مدرسه‌ای که هنوز یادت می‌آد چیه؟",
"59. بهترین غذایی که خودت درست کردی چی بود؟",
"60. آیا وقتی استرس داری، یه روش خاص داری برای آرام شدن؟",
"61. دوست داری وقت آزاد رو چطور بگذرونی؟",
"62. یک کتاب یا فیلم که همیشه دوست داری مرور کنی؟",
"63. آیا تابحال چیزی گفتی که باعث شد کسی ناراحت بشه؟",
"64. بهترین کاری که برای کسی انجام دادی چی بود؟",
"65. اگر می‌تونستی یه روز رو با یه شخصیت معروف بگذرونی، کی رو انتخاب می‌کردی؟",
"66. تا حالا کسی باعث شد خیلی خوشحال بشی؟",
"67. یه عادتی که دوست داری تغییر بدی چیه؟",
"68. چیزی که باعث می‌شه حس گناه داشته باشی چیه؟",
"69. بهترین تصمیمی که اخیراً گرفتی چی بود؟",
"70. یک راز کوچیک درباره خودت که کسی نمی‌دونه چیه؟",
"71. آخرین چیزی که باعث شد بخندی چی بود؟",
"72. وقتی کسی رو تحسین می‌کنی، چه چیزی رو بیشتر می‌بینی؟",
"73. تا حالا یه هدفی داشتی که نتونستی انجام بدی؟",
"74. بهترین خاطره تعطیلاتت چی بود؟",
"75. اگر می‌تونستی یه عادت جدید بسازی، چی می‌ساختی؟",
"76. تا حالا کسی باعث شد یه روزت خراب بشه؟",
"77. چه چیزی باعث می‌شه از چیزی ترس داشته باشی؟",
"78. تا حالا یه راز درباره خودت گفتی که بعد پشیمون شدی؟",
"79. بهترین لحظه با خانواده‌ات چی بود؟",
"80. یه ویژگی که باعث می‌شه مردم تو رو دوست داشته باشن چیه؟",
"81. اولین کسی که دوست داشتی برات پیام بده کی بود؟",
"82. چیزی که باعث شد خیلی خنده‌دار رفتار کنی چی بود؟",
"83. یه عادتی که باعث می‌شه مردم تحسینت کنن چیه؟",
"84. بهترین چیزی که از کسی یاد گرفتی چی بود؟",
"85. یک لحظه رومانتیک که یادت می‌آد بدون گفتن عشق؟",
"86. وقتی کسی غمگین هست، چه کاری می‌کنی؟",
"87. تا حالا کسی باعث شد خیلی خوشحال بشی؟",
"88. چه چیزی باعث می‌شه بیشتر به کسی علاقه‌مند بشی؟",
"89. اولین کسی که دوست داشتی ازت خوشش بیاد کی بود؟",
"90. تا حالا چیزی گفتی ولی بعد پشیمون شدی؟",
"91. یه لحظه‌ای که خنده‌دار و عجیب بود تعریف کن",
"92. بهترین چیزی که باعث شد کسی رو تحسین کنی چی بود؟",
"93. تا حالا کسی باعث شد احساس خاص داشته باشی؟",
"94. وقتی خوشحال هستی، چه کاری انجام می‌دی؟",
"95. یک عادت خوب که بهت کمک می‌کنه چیه؟",
"96. چه چیزی باعث می‌شه حس تنهایی کنی؟",
"97. یه چیزی که همیشه می‌خوای یاد بگیری چیه؟",
"98. وقتی کسی حرفی میزنه که ناراحتت می‌کنه، چه کاری می‌کنی؟",
"99. بهترین خاطره‌ای که با دوستات داشتی چی بود؟",
"100. تا حالا یه تجربه عجیب در سفر داشتی؟",
]

# helper: pick random question
def pick_question():
    return random.choice(QUESTIONS)

# ===== Flask keep-alive server for UptimeRobot =====
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
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

# ===== Main Function =====
def main():
    # Get token from environment variable
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("لطفاً متغیر محیطی TELEGRAM_BOT_TOKEN را تنظیم کنید.")

    # Remove existing webhook to prevent Conflict error
    bot = Bot(token=token)
    bot.delete_webhook()

    # Start Flask keep-alive server
    keep_alive()

    # Build Telegram bot application
    app_bot = ApplicationBuilder().token(token).build()

    # Add handlers
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("question", question_cmd))
    app_bot.add_handler(CallbackQueryHandler(handle_button))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app_bot.add_handler(InlineQueryHandler(inline_query))

    logger.info("Bot is running... Press Ctrl+C to stop it")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
