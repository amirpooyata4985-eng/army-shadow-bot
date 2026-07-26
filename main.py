import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# تنظیمات لاگینگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# اطلاعات ثابت پروژه
TOKEN = "8968244918:AAE3a3lD8qWkTs2YoTd-tiUVzn2wd7aytj4"
SITE_URL = "https://amirpooyata4985-eng.github.io/army-shadow-bot/"

# لینک‌های یوتیوب
NOLAN_YT = "https://youtu.be/sui0polvsxE?si=bP38SdP6VEreRsiJ"
ARCANE_YT = "https://youtu.be/O_yBFlmK2_o?si=k5TA7uAwMvU9KyQV"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /start و نمایش دکمه Analyze"""
    keyboard = [
        [InlineKeyboardButton("Analyze 🎬", callback_data="menu_analyze")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "سلام! به ربات اختصاصی **ارتش سایه‌ها** خوش آمدید. 🎬\n\n"
        "برای دیدن نقدها و بررسی‌های سینمایی، روی دکمه زیر کلیک کنید:"
    )
    
    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /help"""
    help_text = (
        "💡 **راهنمای ربات ارتش سایه‌ها:**\n\n"
        "1️⃣ دکمه **Analyze** را بزنید تا لیست کامل نقدها را ببینید.\n"
        "2️⃣ همچنین می‌توانید نام فیلم یا کارگردان (مثل *نولان* یا *آرکین*) را مستقیم تایپ کنید."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌های شیشه‌ای (Callback Queries)"""
    query = update.callback_query
    await query.answer()

    if query.data == "menu_analyze":
        # منوی اصلی تحلیل‌ها
        keyboard = [
            [InlineKeyboardButton("🎬 دکوپاژ (قسمت ۱): کریستوفر نولان", callback_data="item_nolan")],
            [InlineKeyboardButton("⚔️ مقایسه آرکین و آواتار", callback_data="item_arcane")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="menu_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎬 **لیست تحلیل‌های موجود:**\nلطفاً اثر مورد نظر خود را انتخاب کنید:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    elif query.data == "menu_start":
        await start(update, context)

    elif query.data == "item_nolan":
        # نمایش تحلیل نولان همراه با لینک یوتیوب و لینک مقاله سایت
        text = (
            "🎬 **دکوپاژ (قسمت ۱): کریستوفر نولان و معمای زمان**\n\n"
            "در نخستین قسمت از مجموعه «دکوپاژ» به سراغ کریستوفر نولان رفته‌ایم تا ببینیم "
            "او چگونه با تدوین موازی و روایت غیرخطی، مفهوم زمان را در سینما می‌شکند و ۴ فیلم شاخص او "
            "(تلقین، تنت، ممنتو و میان‌ستاره‌ای) را تحلیل کرده‌ایم."
        )
        keyboard = [
            [InlineKeyboardButton("▶️ تماشا در یوتیوب", url=NOLAN_YT)],
            [InlineKeyboardButton("🌐 خواندن مقاله کامل در سایت", url=SITE_URL)],
            [InlineKeyboardButton("🔙 بازگشت به لیست Analyze", callback_data="menu_analyze")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=False)

    elif query.data == "item_arcane":
        # نمایش تحلیل آرکین همراه با لینک یوتیوب
        text = (
            "⚔️ **تحلیل و مقایسه جامع: آرکین در برابر آواتار**\n\n"
            "در این تحلیل نحوه شخصیت‌پردازی و ساختار روایی دو انیمیشن شاهکار دنیای تصویر یعنی "
            "آرکین و آواتار را با تمرکز بر سیر تحول شخصیت‌هایی مثل جینکس و زوکو بررسی کرده‌ایم."
        )
        keyboard = [
            [InlineKeyboardButton("▶️ تماشا در یوتیوب", url=ARCANE_YT)],
            [InlineKeyboardButton("🔙 بازگشت به لیست Analyze", callback_data="menu_analyze")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=False)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به متنی که کاربر تایپ می‌کند"""
    user_query = update.message.text.strip().lower()

    if any(k in user_query for k in ["نولان", "nolan", "دکوپاژ", "تلقین", "تنت", "ممنتو"]):
        text = (
            "🎬 **دکوپاژ (قسمت ۱): کریستوفر نولان و معمای زمان**\n\n"
            "در نخستین قسمت از مجموعه «دکوپاژ» به سراغ کریستوفر نولان رفته‌ایم تا ببینیم "
            "او چگونه با تدوین موازی و روایت غیرخطی، مفهوم زمان را در سینما می‌شکند."
        )
        keyboard = [
            [InlineKeyboardButton("▶️ تماشا در یوتیوب", url=NOLAN_YT)],
            [InlineKeyboardButton("🌐 خواندن مقاله کامل در سایت", url=SITE_URL)]
        ]
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif any(k in user_query for k in ["آرکین", "آواتار", "arcane", "avatar", "جینکس"]):
        text = (
            "⚔️ **تحلیل و مقایسه جامع: آرکین در برابر آواتار**\n\n"
            "در این تحلیل نحوه شخصیت‌پردازی و ساختار روایی دو انیمیشن شاهکار دنیای تصویر یعنی "
            "آرکین و آواتار را بررسی کرده‌ایم."
        )
        keyboard = [
            [InlineKeyboardButton("▶️ تماشا در یوتیوب", url=ARCANE_YT)]
        ]
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    else:
        keyboard = [
            [InlineKeyboardButton("Analyze 🎬", callback_data="menu_analyze")]
        ]
        await update.message.reply_text(
            "🔍 برای دسترسی سریع‌تر می‌توانید از دکمه **Analyze** استفاده کنید:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # ثبت Handlerها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
    
