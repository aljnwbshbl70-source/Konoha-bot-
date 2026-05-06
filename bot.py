import telebot
import pyrebase
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. إعداد السيرفر المصغر (Keep Alive) لضمان العمل 24 ساعة ---
app = Flask('')

@app.route('/')
def home():
    return "Konoha System is Online! OK"

def run():
    # ريندر يتطلب الحصول على المنفذ من المتغيرات البيئية
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوتات ---
# توكن كونوها (الجديد) - الواجهة التي يستخدمها الناس
KONOHA_TOKEN = '8129323337:AAEXCXQgOZ89gWm3GYmqkPlI8ZSyFC8AzT0'
# توكن يامي (القديم) - المحرك الأساسي للتحميل
YAMI_TOKEN = '8600424985:AAGG-fIEuWBckryg_s8PiHD0UxFSbclQ8hA'

bot = telebot.TeleBot(KONOHA_TOKEN)
yami_engine = telebot.TeleBot(YAMI_TOKEN)

# --- 3. إعدادات Firebase (قاعدة بيانات ريلاتايم) ---
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

# --- 4. معالجة الأوامر ---

@bot.message_handler(commands=['start'])
def start(message):
    try:
        # محاولة جلب الإعدادات من لوحة التحكم (Firebase)
        settings = db.child("bot_settings").get().val()
        
        if settings:
            welcome_text = settings.get('welcome_msg', "مرحباً بك في كونوها Download 🍃\nأرسل رابط الفيديو للتحميل فوراً!")
        else:
            welcome_text = "مرحباً بك في كونوها Download 🍃\nأرسل رابط الفيديو للتحميل فوراً!"
            
        markup = types.InlineKeyboardMarkup()
        
        # إضافة الأزرار من قاعدة البيانات إذا وجدت
        if settings and 'buttons' in settings:
            for btn_name, btn_url in settings['buttons'].items():
                markup.add(types.InlineKeyboardButton(text=btn_name, url=btn_url))
        
        # حقوق المطور (ثابتة)
        markup.add(types.InlineKeyboardButton(text="المطور يامي 🥷", url="https://t.me/Yami_Dev"))
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    except Exception as e:
        print(f"Start Error: {e}")
        bot.send_message(message.chat.id, "مرحباً بك في كونوها Download 🍃\nأرسل الرابط للتحميل.")

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    url = message.text.strip()
    
    if url.startswith("http"):
        status_msg = bot.reply_to(message, "⏳ جاري إرسال الرابط للمحرك... انتظر ثواني.")
        
        # حفظ الطلب في Firebase للرقابة
        try:
            db.child("active_requests").push({
                "user_id": message.chat.id,
                "url": url,
                "status": "processing"
            })
        except:
            pass

        try:
            # إرسال الرابط فقط (مجرداً) للبوت القديم ليبدأ العمل
            yami_engine.send_message(message.chat.id, url)
            bot.edit_message_text("✅ المحرك يعمل الآن، سيصلك الفيديو هنا.", message.chat.id, status_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ حدث خطأ في الربط مع المحرك.", message.chat.id, status_msg.message_id)
            print(f"Engine Link Error: {e}")
    else:
        bot.reply_to(message, "الرجاء إرسال رابط فيديو صحيح (يبدأ بـ http).")

# --- 5. تشغيل النظام ---
if __name__ == "__main__":
    keep_alive() # تشغيل خادم Flask للبقاء مستيقظاً
    print("Konoha Bot is LIVE... 🔥")
    bot.infinity_polling()
            
