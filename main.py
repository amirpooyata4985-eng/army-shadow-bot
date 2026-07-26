import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading data:", e)
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به ربات Cinema Army of Shadows خوش آمدید. 🎬\n\n"
        "نام یک فیلم یا کارگردان (مثلاً نولان) را بفرستید تا تحلیل و ویدیوهای مرتبط را دریافت کنید."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()
    data = load_data()
    found = False

    for item in data:
        keywords = [k.lower() for k in item.get("keywords", [])]
        if any(keyword in user_text for keyword in keywords):
            found = True
            response_text = f"{item['title']}\n\n{item['review']}"
            keyboard = [[InlineKeyboardButton("مشاهده ویدیو 🎥", url=item["video_link"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response_text, reply_markup=reply_markup)
            break

    if not found:
        await update.message.reply_text("متأسفانه تحلیلی برای این کلیدواژه پیدا نشد. کلمه دیگری را امتحان کنید!")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("Bot is running...")
        app.run_polling()
