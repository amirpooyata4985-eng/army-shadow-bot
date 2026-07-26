import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import data_loader

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# آدرس فایل خام داده‌های شما در گیت‌هاب
GITHUB_RAW_URL = "https://raw.githubusercontent.com/amirpooyata4985-eng/army-shadow-bot/main/data.json"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "به ربات کانال یوتیوبی ارتش سایه‌ها خوش آمدید 🎬\n\n"
        "نام یک فیلم یا کارگردان (مثلاً نولان) را بفرستید تا تحلیل و ویدیوهای مرتبط را دریافت کنید."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # جستجو در دیتا از طریق ماژول جدید
    results = data_loader.search(user_text)

    if results:
        for item in results:
            response_text = f"{item['title']}\n\n{item['review']}"
            keyboard = [[InlineKeyboardButton("مشاهده ویدیو 🎥", url=item["video_link"])]]
            await update.message.reply_text(
                response_text, 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await update.message.reply_text("متأسفانه تحلیلی برای این کلیدواژه پیدا نشد.")

if __name__ == "__main__":
    if TOKEN:
        # بارگذاری اولیه اطلاعات از گیت‌هاب / فایل محلی
        data_loader.refresh_data(github_url=GITHUB_RAW_URL, local_path="data.json")
        
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Bot is running with data_loader...")
        app.run_polling()
        
