import telebot
from PIL import Image, ImageEnhance, ImageFilter 
import os
from flask import Flask
from threading import Thread

# Token ekdam sahi hona chahiye
TOKEN = "7859979144:AAEqpEEvtx-2hTtkLcWsydUDSoVLTTtIRyw"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Hi! Photo bhejo, main use Original Size aur High Texture mein convert kar dunga.")

@bot.message_handler(content_types=['photo'])
def photo(msg):
    try:
        # User se photo lena
        file_id = msg.photo[-1].file_id
        file = bot.get_file(file_id)
        data = bot.download_file(file.file_path)

        with open("in.jpg", "wb") as f:
            f.write(data)

        img = Image.open("in.jpg")

        # --- Yahan Quality aur Texture badhaya gaya hai ---
        
        # 1. Sharpness (Skin texture ko ubharne ke liye)
        sharp_enhancer = ImageEnhance.Sharpness(img)
        img = sharp_enhancer.enhance(2.5) # Texture ko thoda hard kiya

        # 2. Detail Filter (Barikiyaan dikhane ke liye)
        img = img.filter(ImageFilter.DETAIL)

        # 3. Contrast (Colors ko crispy banane ke liye)
        con_enhancer = ImageEnhance.Contrast(img)
        img = con_enhancer.enhance(1.15)

        # 4. Save (Quality=100 se original resolution maintain rahega)
        img.save("out.jpg", quality=100, subsampling=0)

        with open("out.jpg", "rb") as f:
            bot.send_photo(msg.chat.id, f, caption="✅ Original Resolution + Texture Applied!")

        # Safayi (Server space ke liye)
        os.remove("in.jpg")
        os.remove("out.jpg")
        
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(msg.chat.id, "Photo process karne mein koi problem aayi.")

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.polling(non_stop=True)
