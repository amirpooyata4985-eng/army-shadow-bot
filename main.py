import json
import logging
import os
import threading
from flask import Flask
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ==================== ۱. وب‌سرور زنده نگه داشتن (UptimeRobot) ====================
app = Flask('')


@app.route('/')
def home():
  return 'Army of Shadows Bot is Live!'


def run_flask():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = threading.Thread(target=run_flask)
  t.daemon = True
  t.start()


# ==================== ۲. تنظیمات لاگ و داده‌ها ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

DATA_URL = 'https://raw.githubusercontent.com/amirpooyata4985-eng/army-shadow-bot/main/data.json'


def load_data():
  try:
    response = requests.get(DATA_URL, timeout=10)
    if response.status_code == 200:
      return response.json()
  except Exception as e:
    logging.error(f'Error fetching data: {e}')

  if os.path.exists('data.json'):
    with open('data.json', 'r', encoding='utf-8') as f:
      return json.load(f)

  return {}


# ==================== ۳. منوها و دکمه‌های اصلی ربات ====================
def get_main_keyboard():
  # چیدمان دقیق طبق دستور شما:
  # اول بخش نقدها، سپس دکوپاژ و آرکین/آواتار
  keyboard = [
      [
          InlineKeyboardButton(
              '📝 آخرین مقالات و نقدها', callback_data='latest_articles'
          )
      ],
      [
          InlineKeyboardButton(
              '🎬 تحلیل‌های دکوپاژ', callback_data='decoupage_section'
          ),
          InlineKeyboardButton(
              '🌀 آرکین و آواتار', callback_data='arcane_avatar_section'
          ),
      ],
      [
          InlineKeyboardButton(
              '🎥 آخرین ویدیوها', callback_data='latest_videos'
          )
      ],
      [
          InlineKeyboardButton(
              '🌐 مشاهده وب‌سایت ارتش سایه‌ها',
              url='https://amirpooyata4985-eng.github.io/army-shadow-bot/',
          )
      ],
  ]
  return InlineKeyboardMarkup(keyboard)


# ==================== ۴. هندلرهای دستورات ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  welcome_text = (
      'سلام! به ربات رسمی کانال **ارتش سایه‌ها (Army of Shadows)** خوش'
      ' آمدید.\n\nاز منوی زیر بخش مورد نظر خود را انتخاب کنید:'
  )
  await update.message.reply_text(
      welcome_text, parse_mode='Markdown', reply_markup=get_main_keyboard()
  )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  help_text = (
      '📌 **راهنمای ربات ارتش سایه‌ها:**\n\n'
      '/start - نمایش منوی اصلی\n'
      '/website - ورود به وب‌سایت'
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
      'برای مطالعه کامل نقدها و مشاهده ویدیوها وارد وب‌سایت شوید:',
      reply_markup=reply_markup,
  )


# مدیریت کلیک روی دکمه‌های شیشه‌ای
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  data = load_data()

  if query.data == 'latest_articles':
    await query.edit_message_text(
        text='📝 **بخش مقالات و نقدها**\n\nبرای مطالعه مقالات کامل روی لینک'
        ' وب‌سایت کلیک کنید.',
        parse_mode='Markdown',
        reply_markup=get_main_keyboard(),
    )
  elif query.data == 'decoupage_section':
    await query.edit_message_text(
        text='🎬 **تحلیل‌های دکوپاژ**\n\nبررسی ساختار کارگردانی و دکوپاژ'
        ' آثار برتر سینما.',
        parse_mode='Markdown',
        reply_markup=get_main_keyboard(),
    )
  elif query.data == 'arcane_avatar_section':
    await query.edit_message_text(
        text='🌀 **تحلیل‌های اختصاصی آرکین و آواتار**\n\nبررسی داستان،'
        ' انیمیشن و جهان‌سازی.',
        parse_mode='Markdown',
        reply_markup=get_main_keyboard(),
    )
  elif query.data == 'latest_videos':
    await query.edit_message_text(
        text='🎥 **آخرین ویدیوهای یوتیوب ارتش سایه‌ها**',
        parse_mode='Markdown',
        reply_markup=get_main_keyboard(),
    )


# ==================== ۵. اجرای اصلی برنامه ====================
def main():
  # روشن کردن وب‌سرور بدون دستکاری منوهای تلگرام
  keep_alive()

  TOKEN = os.environ.get(
      'BOT_TOKEN', '8968244918:AAE3a3lD8qWkTs2YoTd-tiUVzn2wd7aytj4'
  )

  application = Application.builder().token(TOKEN).build()

  # ثبت هندلرها
  application.add_handler(CommandHandler('start', start))
  application.add_handler(CommandHandler('help', help_command))
  application.add_handler(CommandHandler('website', website_command))
  application.add_handler(CallbackQueryHandler(button_callback))

  print('Bot starts running...')
  application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
  main()
  
