import telebot
from PIL import Image
import os  # Yeh zaroori hai
from flask import Flask
from threading import Thread

# TOKEN bilkul sahi hai
TOKEN = "7859979144:AAHAGPi1mgoNdLusIgl96mzOfM5jhem8Ajk"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    # Render ke liye dynamic port settings
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Hi! Photo bhejo")

@bot.message_handler(content_types=['photo'])
def photo(msg):
    try:
        file_id = msg.photo[-1].file_id
        file = bot.get_file(file_id)
        data = bot.download_file(file.file_path)

        with open("in.jpg", "wb") as f:
            f.write(data)

        img = Image.open("in.jpg")
        img = img.resize((800, 800))
        img.save("out.jpg", quality=70)

        with open("out.jpg", "rb") as f:
            bot.send_photo(msg.chat.id, f)

        os.remove("in.jpg")
        os.remove("out.jpg")
    except Exception as e:
        print(f"Error: {e}")

# Sabse important: Bot ko start karna
if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.polling(non_stop=True)
