import telebot
import pyrebase
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. إعداد السيرفر المصغر (Keep Alive) ---
app = Flask('')
@app.route('/')
def home():
    return "Konoha System is Online! OK"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوتات ---
# توكن كونوها (الجديد) - الواجهة
KONOHA_TOKEN = '8129323337:AAEXCXQgOZ89gWm3GYmqkPlI8ZSyFC8AzT0'
# توكن يامي (القديم) - المحرك
YAMI_TOKEN = '8600424985:AAGG-fIEuWBckryg_s8PiHD0UxFSbclQ8hA'

bot = telebot.TeleBot(KONOHA_TOKEN)
yami_engine = telebot.TeleBot(YAMI_TOKEN)

# --- 3. إعدادات Firebase ---
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

# --- 4. منطق البوت (الترحيب والحقوق) ---
@bot.message_handler(commands=['start'])
def start(message):
    # جلب الإعدادات من لوحة التحكم (Firebase)
    settings = db.child("bot_settings").get().val()
    
    welcome_text = settings.get('welcome_msg', "مرحباً بك في كونوها Download 🍃\nأرسل رابط الفيديو للتحميل فوراً!") if settings else "مرحباً بك في كونوها Download 🍃\nأرسل رابط الفيديو للتحميل فوراً!"
    
    markup = types.InlineKeyboardMarkup()
    # إضافة الأزرار من القاعدة (لوحة التحكم)
    if settings and 'buttons' in settings:
        for btn_name, btn_url in settings['buttons'].items():
            markup.add(types.InlineKeyboardButton(text=btn_name, url=btn_url))
    
    # إضافة حقوق المطور بشكل دائم
    markup.add(types.InlineKeyboardButton(text="المطور: يامي 🥷", url="https://t.me/Yami_Dev"))
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    url = message.text.strip() # تنظيف الفراغات
    if "http" in url:
        status_msg = bot.reply_to(message, "⏳ جاري المعالجة عبر محرك كونوها السريع...")
        
        # تخزين الطلب في Firebase ليظهر في لوحة التحكم
        db.child("active_requests").push({
            "user_id": message.chat.id,
            "url": url,
            "status": "processing",
            "bot_source": "Konoha"
        })

        try:
            # التعديل هنا: نرسل الرابط فقط بدون أي نص إضافي
            yami_engine.send_message(message.chat.id, url) 
            
            bot.edit_message_text("✅ تم إرسال الرابط للمحرك، سيصلك الفيديو هنا فور جاهزيته.", message.chat.id, status_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ عذراً، المحرك الأساسي غير متاح حالياً.", message.chat.id, status_msg.message_id)
            print(f"Error sending to engine: {e}")
            
