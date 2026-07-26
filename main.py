import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# تنظیمات لاگین
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# آدرس سایت شما روی گیت‌هاب پیجز
SITE_URL = "https://amirpooyata4985-eng.github.io/army-shadow-bot/"

def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data.json: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به ربات ارتش سایه‌ها خوش آمدید. 🎬\n"
        "نام فیلم، کارگردان یا موضوع مورد نظرتان را بفرستید تا تحلیل آن را برایتان پیدا کنم."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.strip().lower()
    data = load_data()
    found = False

    for item in data:
        keywords = [k.lower() for k in item.get('keywords', [])]
        if any(keyword in user_query for keyword in keywords):
            title = item.get('title', 'تحلیل سینمایی')
            summary = item.get('summary', item.get('review', ''))
            video_link = item.get('video_link', '')

            # ساخت متن پست تلگرام
            caption = f"🎬 **{title}**\n\n{summary}\n\n▶️ [تماشا در یوتیوب]({video_link})"

            # ساخت دکمه شیشه‌ای برای هدایت به سایت
            keyboard = [
                [InlineKeyboardButton("🌐 خواندن نقد کامل در سایت", url=SITE_URL)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text=caption,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            found = True
            break

    if not found:
        await update.message.reply_text("متأسفانه تحلیلی برای این موضوع پیدا نشد. کلمه دیگری را امتحان کنید!")

if __name__ == '__main__':
    # توکن ربات خود را اینجا بگذارید
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()
    
