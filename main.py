import asyncio
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

# ==================== ۱. وب‌سرور برای زنده ماندن ربات در Render ====================
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


# ==================== ۲. تنظیمات و لاگینگ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

DATA_URL = 'https://raw.githubusercontent.com/amirpooyata4985-eng/army-shadow-bot/main/data.json'


# تابع دریافت دیتا (بدون قفل کردن ربات)
def load_data_sync():
  try:
    response = requests.get(DATA_URL, timeout=5)
    if response.status_code == 200:
      return response.json()
  except Exception as e:
    logging.error(f'Error fetching online data: {e}')

  if os.path.exists('data.json'):
    try:
      with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    except Exception as e:
      logging.error(f'Error reading local data.json: {e}')

  return {'videos': [], 'articles': []}


# ==================== ۳. کیبوردها و منوها ====================
def get_main_keyboard():
  keyboard = [
      [InlineKeyboardButton('📝 نقدها', callback_data='reviews_menu')],
      [InlineKeyboardButton('🎥 آخرین ویدیوها', callback_data='latest_videos')],
      [
          InlineKeyboardButton(
              '🌐 ورود به وب‌سایت ارتش سایه‌ها',
              url='https://amirpooyata4985-eng.github.io/army-shadow-bot/',
          )
      ],
  ]
  return InlineKeyboardMarkup(keyboard)


def get_reviews_list_keyboard():
  # لیست دو نقد اختصاصی کانال
  keyboard = [
      [
          InlineKeyboardButton(
              '🎬 دکوپاژ (قسمت اول)', callback_data='review_decoupage'
          )
      ],
      [
          InlineKeyboardButton(
              '🌀 مقایسه آرکین و آواتار (در ۴ پرده)',
              callback_data='review_arcane_avatar',
          )
      ],
      [InlineKeyboardButton('🔙 بازگشت به منوی اصلی', callback_data='main_menu')],
  ]
  return InlineKeyboardMarkup(keyboard)


def get_back_to_reviews_keyboard():
  keyboard = [
      [InlineKeyboardButton('🔙 بازگشت به لیست نقدها', callback_data='reviews_menu')],
      [InlineKeyboardButton('🏠 منوی اصلی', callback_data='main_menu')],
  ]
  return InlineKeyboardMarkup(keyboard)


# ==================== ۴. هندلرها ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  welcome_text = (
      'سلام! به ربات رسمی کانال **ارتش سایه‌ها (Army of Shadows)** خوش'
      ' آمدید.\n\nجهت دسترسی به نقدها و ویدیوها، بخش مورد نظر را انتخاب کنید:'
  )
  await update.message.reply_text(
      welcome_text, parse_mode='Markdown', reply_markup=get_main_keyboard()
  )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  # پاسخ سریع به تلگرام برای جلوگیری از قفل شدن دکمه
  await query.answer()

  # خواندن دیتا در Thread جداگانه برای حفظ سرعت ربات
  data = await asyncio.to_thread(load_data_sync)
  articles = data.get('articles', [])
  videos = data.get('videos', [])

  # ۱. بازگشت به منوی اصلی
  if query.data == 'main_menu':
    await query.edit_message_text(
        text='منوی اصلی ارتش سایه‌ها:', reply_markup=get_main_keyboard()
    )

  # ۲. ورود به لیست نقدها
  elif query.data == 'reviews_menu':
    text = (
        '📝 **بخش نقدها و تحلیل‌ها**\n\nلطفاً نقد مورد نظر خود را برای مشاهده'
        ' انتخاب کنید:'
    )
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_reviews_list_keyboard(),
    )

  # ۳. نقد اول: دکوپاژ قسمت اول (دارای خلاصه + لینک یوتیوب + لینک سایت)
  elif query.data == 'review_decoupage':
    # پیدا کردن اطلاعات نقد دکوپاژ از دیتا
    item = next(
        (a for a in articles if 'دکوپاژ' in a.get('title', '')),
        {
            'title': 'دکوپاژ (قسمت اول)',
            'summary': 'تحلیل و بررسی ساختار دکوپاژ و میزانسن در سینما.',
            'video_link': 'https://youtube.com',
            'link': 'https://amirpooyata4985-eng.github.io/army-shadow-bot/',
        },
    )

    text = f"🎬 **{item.get('title', 'دکوپاژ (قسمت اول)')}**\n\n"
    text += f"📝 **خلاصه:**\n{item.get('summary', '')}\n\n"

    video_url = item.get('video_link') or item.get('video_url', '')
    site_url = item.get('link', '')

    if video_url:
      text += f'🎥 [تماشای ویدیو در یوتیوب]({video_url})\n'
    if site_url:
      text += f'🌐 [مطالعه کامل مقاله در وب‌سایت]({site_url})\n'

    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_back_to_reviews_keyboard(),
        disable_web_page_preview=True,
    )

  # ۴. نقد دوم: مقایسه آرکین و آواتار (دارای خلاصه + لینک یوتیوب)
  elif query.data == 'review_arcane_avatar':
    item = next(
        (
            a
            for a in articles
            if 'آرکین' in a.get('title', '') or 'آواتار' in a.get('title', '')
        ),
        {
            'title': 'مقایسه‌ای در چهار پرده: آرکین و آواتار',
            'summary': (
                'تحلیل تطبیقی جهان‌سازی، شخصیت‌پردازی و ساختار روایی دو انیمیشن'
                ' شاهکار آرکین و آواتار.'
            ),
            'video_link': 'https://youtube.com',
        },
    )

    text = f"🌀 **{item.get('title', 'مقایسه آرکین و آواتار')}**\n\n"
    text += f"📝 **خلاصه:**\n{item.get('summary', '')}\n\n"

    video_url = item.get('video_link') or item.get('video_url', '')
    if video_url:
      text += f'🎥 [تماشای ویدیو در یوتیوب]({video_url})\n'

    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_back_to_reviews_keyboard(),
        disable_web_page_preview=True,
    )

  # ۵. بخش آخرین ویدیوها
  elif query.data == 'latest_videos':
    text = '🎥 **آخرین ویدیوهای یوتیوب:**\n\n'
    if not videos:
      text += 'ویدیویی ثبت نشده است.'
    else:
      for v in videos:
        text += (
            f"🎬 **{v.get('title', '')}**\n🔗"
            f" [تماشا در یوتیوب]({v.get('url', '')})\n───────────────\n"
        )

    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                '🔙 بازگشت به منوی اصلی', callback_data='main_menu'
            )
        ]]),
        disable_web_page_preview=True,
    )


# ==================== ۵. اجرای اصلی ====================
def main():
  keep_alive()

  TOKEN = os.environ.get(
      'BOT_TOKEN', '8968244918:AAE3a3lD8qWkTs2YoTd-tiUVzn2wd7aytj4'
  )
  application = Application.builder().token(TOKEN).build()

  application.add_handler(CommandHandler('start', start))
  application.add_handler(CallbackQueryHandler(button_callback))

  print('Bot is running with smooth Async handlers...')
  application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
  main()
    
