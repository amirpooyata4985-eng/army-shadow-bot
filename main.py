import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import data_loader

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GITHUB_RAW_URL = "https://raw.githubusercontent.com/amirpooyata4985-eng/army-shadow-bot/main/data.json"

HELP_TEXT = (
    "📖 **راهنمای استفاده از ربات ارتش سایه‌ها (Army of Shadows)**\n\n"
    "۱. **جستجوی مستقیم:** کافی است اسم یک کارگردان (مثلاً نولان، تارکوفسکی) یا عنوان یک فیلم/قسمت را بفرستید تا تحلیل و لینک ویدیوی آن برایتان ارسال شود.\n"
    "۲. **مشاهده همه‌ی نقدها:** با زدن دکمه «لیست همه‌ی نقدها 📊» می‌توانید تمامی تحلیل‌های موجود را یکجا مطالعه کنید.\n"
    "۳. **دستورات سریع:**\n"
    "• /start — شروع مجدد ربات و مشاهده منوی اصلی\n"
    "• /help — دریافت همین راهنما"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("لیست همه‌ی نقدها و تحلیل‌ها 📊 (Analyze)", callback_data="show_all_reviews")],
        [InlineKeyboardButton("راهنمای استفاده 💡 (Help)", callback_data="show_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "به ربات کانال یوتیوبی ارتش سایه‌ها خوش آمدید 🎬\n\n"
        "نام یک فیلم یا کارگردان (مثلاً نولان) را بفرستید، یا از دکمه‌های زیر استفاده کنید:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_all_reviews":
        all_entries = data_loader.get_all_entries()

        if not all_entries:
            await query.message.reply_text("هنوز تحلیلی در دیتابیس ثبت نشده است.")
            return

        await query.message.reply_text("📚 **لیست تمامی تحلیل‌های موجود در کانال ارتش سایه‌ها:**")
        for item in all_entries:
            response_text = f"{item['title']}\n\n{item['review']}"
            btn = [[InlineKeyboardButton("مشاهده ویدیو 🎥", url=item["video_link"])]]
            await query.message.reply_text(response_text, reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == "show_help":
        await query.message.reply_text(HELP_TEXT, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    results = data_loader.search(user_text)

    if results:
        for item in results:
            response_text = f"{item['title']}\n\n{item['review']}"
            keyboard = [[InlineKeyboardButton("مشاهده ویدیو 🎥", url=item["video_link"])]]
            await update.message.reply_text(response_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("متأسفانه تحلیلی برای این کلیدواژه پیدا نشد. برای راهنمایی بیشتر /help را بفرستید.")

if __name__ == "__main__":
    if TOKEN:
        data_loader.refresh_data(github_url=GITHUB_RAW_URL, local_path="data.json")
        
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CallbackQueryHandler(handle_button))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Bot is running...")
        app.run_polling()
        
