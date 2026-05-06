import telebot
import os
import yt_dlp
import pyrebase
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. إعداد السيرفر المصغر للبقاء 24 ساعة ---
app = Flask('')
@app.route('/')
def home(): return "Konoha Engine is Active! OK"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. إعدادات البوت وفيربايس ---
TOKEN = '8129323337:AAEXCXQgOZ89gWm3GYmqkPlI8ZSyFC8AzT0'
bot = telebot.TeleBot(TOKEN)

config = {
    "apiKey": "AIzaSyCGhyt2eEFtA1nRiq8Km8jPLCvBtcxdGBg",
    "authDomain": "konoha-bot-b61e1.firebaseapp.com",
    "databaseURL": "https://konoha-bot-b61e1-default-rtdb.firebaseio.com/",
    "projectId": "konoha-bot-b61e1",
    "storageBucket": "konoha-bot-b61e1.firebasestorage.app",
    "appId": "1:389753511382:web:0cddef8e065762f9bc9877"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# --- 3. دالة التحميل ---
def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'video_%(id)s.mp4',
        'max_filesize': 48 * 1024 * 1024,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# --- 4. معالجة الرسائل ---
@bot.message_handler(commands=['start'])
def start(message):
    settings = db.child("bot_settings").get().val()
    welcome_text = settings.get('welcome_msg', "مرحباً بك في كونوها Download 🍃") if settings else "مرحباً بك في كونوها Download 🍃"
    
    markup = types.InlineKeyboardMarkup()
    if settings and 'buttons' in settings:
        for btn_name, btn_url in settings['buttons'].items():
            markup.add(types.InlineKeyboardButton(text=btn_name, url=btn_url))
    markup.add(types.InlineKeyboardButton(text="المطور يامي 🥷", url="https://t.me/Yami_Dev"))
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "http" in url:
        status = bot.reply_to(message, "⏳ جاري التحميل... انتظر ثواني.")
        try:
            filename = download_video(url)
            with open(filename, 'rb') as v:
                bot.send_video(message.chat.id, v, caption="تم التحميل بواسطة كونوها 🍃")
            os.remove(filename)
            bot.delete_message(message.chat.id, status.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ خطأ: تأكد من الرابط أو حجم الفيديو.", message.chat.id, status.message_id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
    
