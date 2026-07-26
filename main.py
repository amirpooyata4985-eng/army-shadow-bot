import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

HELP_TEXT = (
    "📖 **راهنمای استفاده از ربات ارتش سایه‌ها (Army of Shadows)**\n\n"
    "۱. **جستجوی مستقیم:** کافی است اسم یک کارگردان (مثلاً نولان، تارکوفسکی) یا عنوان یک فیلم/قسمت را بفرستید تا تحلیل و لینک ویدیوی آن برایتان ارسال شود.\n"
    "۲. **مشاهده همه‌ی نقدها:** با زدن دکمه «لیست همه‌ی نقدها 📊» یا ارسال دستور /analyze می‌توانید تمامی تحلیل‌های موجود را یکجا مطالعه کنید.\n"
    "۳. **دستورات سریع:**\n"
    "• /start — شروع مجدد ربات و مشاهده منوی اصلی\n"
    "• /analyze — مشاهده یکجای تمام نقدها\n"
    "• /help — دریافت همین راهنما"
)

def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading data.json:", e)
        return []

async def send_all_reviews(update: Update):
    data = load_data()
    target = update.message if update.message else update.callback_query.message

    if not data:
        await target.reply_text("هنوز تحلیلی در دیتابیس ثبت نشده است.")
        return

    await target.reply_text("📚 **لیست تمامی تحلیل‌های موجود در کانال ارتش سایه‌ها:**")
    for item in data:
        response_text = f"{item['title']}\n\n{item['review']}"
        btn = [[InlineKeyboardButton("مشاهده ویدیو 🎥", url=item["video_link"])]]
        await target.reply_text(response_text, reply_markup=InlineKeyboardMarkup(btn))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("لیست همه‌ی نقدها و تحلیل‌ها 📊 (Analyze)", callback_data="show_all_reviews")],
        [InlineKeyboardButton("راهنمای استفاده 💡 (Help)", callback_data="show_help")]
    ]
    await update.message.reply_text(
        "به ربات کانال یوتیوبی ارتش سایه‌ها خوش آمدید 🎬\n\n"
        "نام یک فیلم یا کارگردان (مثلاً نولان) را بفرستید، یا از دکمه‌های زیر استفاده کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_all_reviews(update)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_all_reviews":
        await send_all_reviews(update)
    elif query.data == "show_help":
        await query.message.reply_text(HELP_TEXT, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()
    data = load_data()
    found = False

    for item in data:
        keywords = [k.lower() for k in item.get("keywords", [])]
        title = item.get("title", "").lower()
        if any(kw in user_text for kw in keywords) or user_text in title:
            found = True
            response_text = f"{item['title']}\n\n{item['review']}"
            keyboard = [[InlineKeyboardButton("مشاهده ویدیو 🎥", url=item["video_link"])]]
            await update.message.reply_text(response_text, reply_markup=InlineKeyboardMarkup(keyboard))
            break

    if not found:
        await update.message.reply_text("متأسفانه تحلیلی برای این کلیدواژه پیدا نشد. برای راهنمایی بیشتر /help را بفرستید.")

if __name__ == "__main__":
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("analyze", analyze_command))
        app.add_handler(CallbackQueryHandler(handle_button))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Bot is running...")
        app.run_polling()
        
