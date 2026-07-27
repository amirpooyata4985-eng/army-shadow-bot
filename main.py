import asyncio
import json
import logging
import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ==================== ۱. تنظیمات لاگینگ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

DATA_URL = 'https://raw.githubusercontent.com/amirpooyata4985-eng/army-shadow-bot/main/data.json'


# ==================== ۲. فراخوانی داده‌ها ====================
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


# ==================== ۳. چیدمان کیبوردها ====================
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
      'سلام! به ربات رسمی کانال <b>ارتش سایه‌ها (Army of Shadows)</b> خوش'
      ' آمدید.\n\nجهت دسترسی به نقدها و ویدیوها، بخش مورد نظر را انتخاب کنید:'
  )
  await update.message.reply_text(
      welcome_text, parse_mode='HTML', reply_markup=get_main_keyboard()
  )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  try:
    data = await asyncio.to_thread(load_data_sync)
    articles = data.get('articles', [])
    videos = data.get('videos', [])

    # بازگشت به منوی اصلی
    if query.data == 'main_menu':
      await query.edit_message_text(
          text='منوی اصلی ارتش سایه‌ها:', reply_markup=get_main_keyboard()
      )

    # ورود به منوی لیست نقدها
    elif query.data == 'reviews_menu':
      text = (
          '📝 <b>بخش نقدها و تحلیل‌ها</b>\n\nلطفاً نقد مورد نظر خود را انتخاب'
          ' کنید:'
      )
      await query.edit_message_text(
          text=text, parse_mode='HTML', reply_markup=get_reviews_list_keyboard()
      )

    # نقد اول: دکوپاژ (خلاصه + لینک یوتیوب + لینک وب‌سایت)
    elif query.data == 'review_decoupage':
      item = next(
          (a for a in articles if 'دکوپاژ' in a.get('title', '')),
          {
              'title': 'دکوپاژ (قسمت اول)',
              'summary': 'تحلیل و بررسی ساختار دکوپاژ و میزانسن در سینما.',
              'video_link': 'https://youtube.com',
              'link': (
                  'https://amirpooyata4985-eng.github.io/army-shadow-bot/'
              ),
          },
      )

      title = item.get('title', 'دکوپاژ (قسمت اول)')
      summary = item.get('summary', '')
      video_url = item.get('video_link') or item.get('video_url', '')
      site_url = item.get('link', '')

      text = f'🎬 <b>{title}</b>\n\n'
      if summary:
        text += f'📝 <b>خلاصه:</b>\n{summary}\n\n'
      if video_url:
        text += f'🎥 <a href="{video_url}">تماشای ویدیو در یوتیوب</a>\n'
      if site_url:
        text += f'🌐 <a href="{site_url}">مطالعه کامل مقاله در وب‌سایت</a>\n'

      await query.edit_message_text(
          text=text,
          parse_mode='HTML',
          reply_markup=get_back_to_reviews_keyboard(),
          disable_web_page_preview=True,
      )

    # نقد دوم: آرکین و آواتار (خلاصه + لینک یوتیوب)
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
                  'تحلیل تطبیقی جهان‌سازی، شخصیت‌پردازی و ساختار روایی دو'
                  ' انیمیشن شاهکار آرکین و آواتار.'
              ),
              'video_link': 'https://youtube.com',
          },
      )

      title = item.get('title', 'مقایسه‌ای در چهار پرده: آرکین و آواتار')
      summary = item.get('summary', '')
      video_url = item.get('video_link') or item.get('video_url', '')

      text = f'🌀 <b>{title}</b>\n\n'
      if summary:
        text += f'📝 <b>خلاصه:</b>\n{summary}\n\n'
      if video_url:
        text += f'🎥 <a href="{video_url}">تماشای ویدیو در یوتیوب</a>\n'

      await query.edit_message_text(
          text=text,
          parse_mode='HTML',
          reply_markup=get_back_to_reviews_keyboard(),
          disable_web_page_preview=True,
      )

    # آخرین ویدیوها
    elif query.data == 'latest_videos':
      text = '🎥 <b>آخرین ویدیوهای یوتیوب:</b>\n\n'
      if not videos:
        text += 'ویدیویی ثبت نشده است.'
      else:
        for v in videos:
          v_title = v.get('title', 'ویدیو')
          v_url = v.get('url', '')
          text += (
              f'🎬 <b>{v_title}</b>\n🔗 <a href="{v_url}">تماشا در'
              ' یوتیوب</a>\n───────────────\n'
          )

      await query.edit_message_text(
          text=text,
          parse_mode='HTML',
          reply_markup=InlineKeyboardMarkup([[
              InlineKeyboardButton(
                  '🔙 بازگشت به منوی اصلی', callback_data='main_menu'
              )
          ]]),
          disable_web_page_preview=True,
      )

  except Exception as e:
    logging.error(f'Error processing callback query: {e}')


# ==================== ۵. اجرای اصلی ====================
def main():
  TOKEN = os.environ.get(
      'BOT_TOKEN', '8968244918:AAE3a3lD8qWkTs2YoTd-tiUVzn2wd7aytj4'
  )
  application = Application.builder().token(TOKEN).build()

  application.add_handler(CommandHandler('start', start))
  application.add_handler(CallbackQueryHandler(button_callback))

  print('Pure Telegram Bot is running...')
  application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
  main()
    
