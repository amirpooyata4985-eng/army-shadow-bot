import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

HELP_TEXT = (
    "📖 **راهنمای استفاده از ربات ارتش سایه‌ها (Army of Shadows)**\n\n"
    "۱. **جستجوی مستقیم:** کافی است اسم یک کارگردان (مثلاً نولان) یا یک اثر را بفرستید تا تحلیل و لینک ویدیو ارسال شود.\n"
    "۲. **مشاهده همه‌ی نقدها:** با زدن دکمه «لیست همه‌ی نقدها 📊» یا ارسال دستور /analyze می‌توانید لیست موضوعات را ببینید.\n"
    "۳. **دستورات سریع:**\n"
    "• /start — شروع مجدد ربات و منوی اصلی\n"
    "• /analyze — لیست نقدها و تحلیل‌ها\n"
    "• /help — راهنمای استفاده"
)

def load_data():
    """خواندن اطلاعات از data.json"""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading data.json:", e)
        return []

async def show_analysis_menu(update: Update):
    """ایجاد منوی دکمه‌ای خلاصه از پروژه‌ها"""
    data = load_data()
    target = update.message if update.message else update.callback_query.message

    if not data:
        await target.reply_text("هنوز تحلیلی در دیتابیس ثبت نشده است.")
        return

    keyboard = []
    for index, item in enumerate(data):
        button_text = item.get("title", f"تحلیل {index + 1}")
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"review_{index}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await target.reply_text("📊 **موضوع مورد نظر خود را انتخاب کنید:**", reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("لیست همه‌ی نقدها 📊", callback_data="show_all_reviews")],
        [InlineKeyboardButton("راهنما 💡", callback_data="show_help")]
    ]
    await update.message.reply_text(
        "به ربات کانال یوتیوبی ارتش سایه‌ها خوش آمدید 🎬\n\n"
        "نام یک اثر یا کارگردان را بفرستید، یا از دکمه‌های زیر استفاده کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_analysis_menu(update)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_all_reviews":
        await show_analysis_menu(update)

    elif query.data == "show_help":
        await query.message.reply_text(HELP_TEXT, parse_mode="Markdown")

    elif query.data.startswith("review_"):
        index = int(query.data.split("_")[1])
        data = load_data()

        if 0 <= index < len(data):
            item = data[index]
            response_text = f"🎬 **{item['title']}**\n\n{item['review']}"
            keyboard = [[InlineKeyboardButton("مشاهده ویدیو 🎥", url=item["video_link"])]]
            await query.message.reply_text(response_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()
    data = load_data()
    found = False

    for item in data:
        keywords = [k.lower() for k in item.get("keywords", [])]
        title = item.get("title", "").lower()
        if any(kw in user_text for kw in keywords) or user_text in title:
            found = True
            response_text = f"🎬 **{item['title']}**\n\n{item['review']}"
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
        
