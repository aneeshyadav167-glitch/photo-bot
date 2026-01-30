import telebot
from PIL import Image
import os
from flask import Flask
from threading import Thread

TOKEN = "7859979144: AAEqpEEvtx-2hTtkLcWsydUDSo
VLTTtIRyw"

bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id,"Hi! Photo bhejo 📸")

@bot.message_handler(content_types=['photo'])
def photo(msg):

    file_id = msg.photo[-1].file_id
    file = bot.get_file(file_id)
    data = bot.download_file(file.file_path)

    with open("in.jpg","wb") as f:
        f.write(data)

    img = Image.open("in.jpg")
    img = img.resize((800,800))
    img.save("out.jpg",quality=70)

    with open("out.jpg","rb") as f:
        bot.send_photo(msg.chat.id,f)

    os.remove("in.jpg")
    os.remove("out.jpg")

keep_alive()
bot.polling()
