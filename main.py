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

# ==================== ۱. وب‌سرور برای زنده ماندن ربات ====================
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

# ==================== ۲. تنظیمات و دیتابیس ====================
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
    logging.error(f'Error fetching online data: {e}')

  if os.path.exists('data.json'):
    with open('data.json', 'r', encoding='utf-8') as f:
      return json.load(f)

  return {'videos': [], 'articles': []}

# ==================== ۳. کیبوردهای اصلی ====================
def get_main_keyboard():
  keyboard = [
      # ردیف اول: فقط نقدها
      [InlineKeyboardButton('📝 نقدها', callback_data='all_reviews_list')],
      # ردیف دوم: دکوپاژ و آرکین/آواتار در کنار هم
      [
          InlineKeyboardButton('🎬 تحلیل‌های دکوپاژ', callback_data='decoupage_section'),
          InlineKeyboardButton('🌀 آرکین و آواتار', callback_data='arcane_avatar_section'),
      ],
      # ردیف سوم و چهارم: ویدیوها و سایت
      [InlineKeyboardButton('🎥 آخرین ویدیوها', callback_data='latest_videos')],
      [InlineKeyboardButton('🌐 ورود به وب‌سایت ارتش سایه‌ها', url='https://amirpooyata4985-eng.github.io/army-shadow-bot/')],
  ]
  return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
  return InlineKeyboardMarkup([[InlineKeyboardButton('🔙 بازگشت به منوی اصلی', callback_data='main_menu')]])

# ==================== ۴. هندلرهای دکمه‌ها ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  welcome_text = (
      'سلام! به ربات رسمی کانال **ارتش سایه‌ها (Army of Shadows)** خوش آمدید.\n\n'
      'جهت دسترسی به نقدها و ویدیوها، بخش مورد نظر را انتخاب کنید:'
  )
  await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=get_main_keyboard())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  data = load_data()
  articles = data.get('articles', [])
  videos = data.get('videos', [])

  if query.data == 'main_menu':
    await query.edit_message_text('منوی اصلی ارتش سایه‌ها:', reply_markup=get_main_keyboard())

  # === بخش تمامی نقدها (دکمه اول) ===
  elif query.data == 'all_reviews_list':
    if not articles:
      text = 'هنوز مقاله‌ای ثبت نشده است.'
    else:
      text = '📚 **تمامی نقدها:**\n\n'
      for item in articles:
        title = item.get('title', 'بدون عنوان')
        summary = item.get('summary', '')
        
        # دریافت لینک سایت و لینک ویدیو از فایل جیسون
        site_link = item.get('link', '')
        video_link = item.get('video_link', '') or item.get('video_url', '')

        text += f'🔹 **{title}**\n'
        if summary:
          text += f'📝 {summary}\n'
        if video_link:
          text += f'🎥 [تماشای ویدیو در یوتیوب]({video_link})\n'
        if site_link:
          text += f'🌐 [مطالعه کامل مقاله در سایت]({site_link})\n'
        text += '───────────────\n'

    await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=get_back_keyboard(), disable_web_page_preview=True)

  # === بخش دکوپاژ ===
  elif query.data == 'decoupage_section':
    decoupage_items = [a for a in articles if 'دکوپاژ' in a.get('title', '') or 'دکوپاژ' in a.get('category', '')]
    if not decoupage_items:
      decoupage_items = articles[:3] # اگر دسته‌بندی نبود پیش‌فرض چندتای اول را بیاورد

    text = '🎬 **تحلیل‌های دکوپاژ:**\n\n'
    if not decoupage_items:
      text += 'محتوایی در این بخش یافت نشد.'
    else:
      for item in decoupage_items:
        text += f"🔹 **{item.get('title', '')}**\n{item.get('summary', '')}\n🔗 [مشاهده کامل]({item.get('link', '')})\n───────────────\n"
    await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=get_back_keyboard(), disable_web_page_preview=True)

  # === بخش آرکین و آواتار ===
  elif query.data == 'arcane_avatar_section':
    filtered_items = [a for a in articles if any(k in a.get('title', '').lower() or k in a.get('summary', '').lower() for k in ['آرکین', 'آواتار', 'arcane', 'avatar'])]
    text = '🌀 **تحلیل‌های آرکین و آواتار:**\n\n'
    if not filtered_items:
      text += 'هنوز تحلیلی برای آرکین یا آواتار ثبت نشده است.'
    else:
      for item in filtered_items:
        text += f"🔹 **{item.get('title', '')}**\n{item.get('summary', '')}\n🔗 [مشاهده کامل]({item.get('link', '')})\n───────────────\n"
    await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=get_back_keyboard(), disable_web_page_preview=True)

  # === بخش ویدیوها ===
  elif query.data == 'latest_videos':
    text = '🎥 **آخرین ویدیوها:**\n\n'
    if not videos:
      text += 'ویدیویی ثبت نشده است.'
    else:
      for v in videos:
        text += f"🎬 **{v.get('title', '')}**\n🔗 [تماشا در یوتیوب]({v.get('url', '')})\n───────────────\n"
    await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=get_back_keyboard(), disable_web_page_preview=True)

# ==================== ۵. اجرای اصلی ====================
def main():
  keep_alive()
  TOKEN = os.environ.get('BOT_TOKEN', '8968244918:AAE3a3lD8qWkTs2YoTd-tiUVzn2wd7aytj4')
  application = Application.builder().token(TOKEN).build()
  application.add_handler(CommandHandler('start', start))
  application.add_handler(CallbackQueryHandler(button_callback))
  
  print('Bot running with updated menus and video links...')
  application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
  main()
    
