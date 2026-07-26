import json
import logging
import os
import threading
from flask import Flask
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==================== ۱. وب‌سرور برای زنده نگه داشتن سرور ====================
app = Flask('')


@app.route('/')
def home():
  return 'Army of Shadows Bot is Live and Running!'


def run_flask():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = threading.Thread(target=run_flask)
  t.daemon = True
  t.start()


# ==================== ۲. تنظیمات لاگینگ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# لینک فایل data.json روی گیت‌هاب (ریپازیتوری شما)
DATA_URL = 'https://raw.githubusercontent.com/amirpooyata4985-eng/army-shadow-bot/main/data.json'


# ==================== ۳. توابع دریافت داده ====================
def load_data():
  try:
    response = requests.get(DATA_URL, timeout=10)
    if response.status_code == 200:
      return response.json()
  except Exception as e:
    logging.error(f'Error fetching data from URL: {e}')

  # اگر دریافت آنلاین موفق نبود، فایل محلی را می‌خواند
  if os.path.exists('data.json'):
    with open('data.json', 'r', encoding='utf-8') as f:
      return json.load(f)

  return {'videos': [], 'articles': []}


# ==================== ۴. هندلرهای دستورات تلگرام ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [
      [
          InlineKeyboardButton(
              '🎬 آخرین ویدیوها', callback_data='latest_videos'
          )
      ],
      [
          InlineKeyboardButton(
              '📝 آخرین مقالات و نقدها', callback_data='latest_articles'
          )
      ],
      [
          InlineKeyboardButton(
              '🌐 مشاهده وب‌سایت',
              url='https://amirpooyata4985-eng.github.io/army-shadow-bot/',
          )
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  welcome_text = (
      'سلام! به ربات کانال **ارتش سایه‌ها (Army of Shadows)** خوش آمدید.\n\n'
      'از طریق دکمه‌های زیر می‌توانید به آخرین نقدها، تحلیلی‌های سینمایی و ویدیوهای ما دسترسی داشته باشید:'
  )
  await update.message.reply_text(
      welcome_text, parse_mode='Markdown', reply_markup=reply_markup
  )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  help_text = (
      '📌 **راهنمای ربات:**\n\n'
      '/start - شروع مجدد ربات و نمایش منو\n'
      '/latest - دریافت آخرین محتوای منتشر شده\n'
      '/website - لینک مستقیم وب‌سایت'
  )
  await update.message.reply_text(help_text, parse_mode='Markdown')


async def website_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [[
      InlineKeyboardButton(
          '🌐 ورود به وب‌سایت',
          url='https://amirpooyata4985-eng.github.io/army-shadow-bot/',
      )
  ]]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text(
      'برای مشاهده تمامی مقالات و ویدیوها وارد وب‌سایت شوید:',
      reply_markup=reply_markup,
  )


# ==================== ۵. تابع اصلی اجرای ربات ====================
def main():
  # ۱. روشن کردن وب‌سرور Flask در پس‌زمینه
  keep_alive()

  # ۲. توکن ربات (از Environment Variables یا مقدار مستقیم)
  TOKEN = os.environ.get(
      'BOT_TOKEN', '8968244918:AAE3a3lD8qWkTs2YoTd-tiUVzn2wd7aytj4'
  )  # توکن خود را در صورت نیاز چک کنید

  application = Application.builder().token(TOKEN).build()

  # ثبت دستورات
  application.add_handler(CommandHandler('start', start))
  application.add_handler(CommandHandler('help', help_command))
  application.add_handler(CommandHandler('website', website_command))

  print('Bot is running with web server enabled...')
  application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
  main()
    
