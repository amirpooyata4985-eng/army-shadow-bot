import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# تنظیمات لاگین برای بررسی خطاهای احتمالی
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# آدرس وب‌سایت در گیت‌هاب پیجز
SITE_URL = "https://amirpooyata4985-eng.github.io/army-shadow-bot/"

def load_data():
    """خواندن اطلاعات از فایل data.json"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data.json: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /start"""
    user_name = update.effective_user.first_name
    welcome_text = (
        f"سلام {user_name} عزیز! 🎬\n"
        "به ربات اختصاصی **ارتش سایه‌ها** خوش آمدید.\n\n"
        "اینجا می‌توانید تحلیل‌های سینمایی، بررسی آثار کارگردانان بزرگ و مقایسه انیمیشن‌ها را پیدا کنید.\n\n"
        "📌 **راهنما:** کافیست نام فیلم، کارگردان یا موضوع مورد نظرتان (مثلاً: *نولان* یا *آرکین*) را بفرستید.\n"
        "برای دیدن راهنمای کامل دستور /help را ارسال کنید."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /help"""
    help_text = (
        "💡 **راهنمای استفاده از ربات ارتش سایه‌ها:**\n\n"
        "1️⃣ **جستجوی تحلیل‌ها:**\n"
        "اسم فیلم یا کارگردان را تایپ کنید (مثلاً: `نولان`، `تلقین`، `آرکین`).\n\n"
        "2️⃣ **خواندن مقالات کامل:**\n"
        "زیر هر تحلیل، دکمه‌ای به اسم 🌐 *خواندن نقد کامل در سایت* وجود دارد که مقاله کامل را در وب‌سایت ما به شما نشان می‌دهد.\n\n"
        "3️⃣ **تماشا در یوتیوب:**\n"
        "اگر تحلیلی دارای ویدیوی یوتیوب باشد، لینک مستقیم آن در پیام قرار می‌گیرد."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش متن‌های فرستاده شده و جستجو در data.json"""
    user_query = update.message.text.strip().lower()
    data = load_data()
    found = False

    for item in data:
        keywords = [k.lower() for k in item.get('keywords', [])]
        # بررسی وجود کلیدواژه در متن کاربر
        if any(keyword in user_query for keyword in keywords):
            title = item.get('title', 'تحلیل سینمایی')
            summary = item.get('summary', item.get('review', ''))
            video_link = item.get('video_link', '')

            # ساخت متن پست
            caption = f"🎬 **{title}**\n\n{summary}"
            if video_link:
                caption += f"\n\n▶️ [تماشا در یوتیوب]({video_link})"

            # دکمه شیشه‌ای هدایت به سایت
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
        await update.message.reply_text(
            "🔍 متأسفانه تحلیلی برای این موضوع پیدا نشد.\n"
            "لطفاً کلمات دیگری مثل **نولان** یا **آرکین** را امتحان کنید یا دستور /help را بفرستید."
        )

if __name__ == '__main__':
    # توکن ربات شما
    TOKEN = "8968244918:AAE3a3lD8qWkTs2YoTd-tiUVzn2wd7aytj4"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ثبت دستورات (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()
    
