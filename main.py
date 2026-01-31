import telebot
import cv2
import numpy as np
import os
from PIL import Image, ImageEnhance, ImageFilter
from flask import Flask
from threading import Thread

# --- SETUP ---
TOKEN = "8416936551:AAFmNH1lpMv7md0GW9FkSWIarPo-dQsZmmw"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Multi-Stage Pro Engine is Live"

def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run).start()

# --- STAGE 1: RGB CHANNEL SPLITTING & ENHANCEMENT ---
def step_rgb_enhance(img):
    # Photo ko 3 primary colors mein todna
    b, g, r = cv2.split(img)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    # Har color channel ko alag se process karna (Hosting load balance)
    r_en = clahe.apply(r)
    g_en = clahe.apply(g)
    b_en = clahe.apply(b)
    return cv2.merge((b_en, g_en, r_en))

# --- STAGE 2: 9-TILE PIECE-BY-PIECE ANALYSIS ---
def step_tile_processing(img):
    h, w = img.shape[:2]
    # Manual Upscaling to 2x for detail measurement
    img_big = cv2.resize(img, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
    h2, w2 = img_big.shape[:2]
    
    # 9 Pices (Tiles) mein divide karke process karna
    th, tw = h2//3, w2//3
    for y in range(3):
        for x in range(3):
            y1, y2 = y*th, (y+1)*th
            x1, x2 = x*tw, (x+1)*tw
            tile = img_big[y1:y2, x1:x2]
            # Detail measurement and texture pop
            tile = cv2.detailEnhance(tile, sigma_s=15, sigma_r=0.15)
            img_big[y1:y2, x1:x2] = tile
    return img_big

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "💎 *Pro-Stage Image Engine Active*\n\nBhejiye photo, main use 4-Stages mein process karunga:\n1️⃣ RGB Color Splitting\n2️⃣ 9-Piece Tile Analysis\n3️⃣ High-Level Detail Assembly\n4️⃣ Final Touchup", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    try:
        sent_msg = bot.reply_to(msg, "🛠 *Processing...*\nStage 1/4: RGB Splitting...", parse_mode="Markdown")
        
        file_info = bot.get_file(msg.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        with open("raw.jpg", "wb") as f: f.write(data)

        # STAGE 1 & 2: Colors and Tiles
        img = cv2.imread("raw.jpg")
        bot.edit_message_text("🛠 *Processing...*\nStage 2/4: 9-Tile Detailed Analysis...", msg.chat.id, sent_msg.message_id, parse_mode="Markdown")
        img = step_rgb_enhance(img)
        img = step_tile_processing(img)
        
        # STAGE 3: Assembly & Edge Smoothing
        bot.edit_message_text("🛠 *Processing...*\nStage 3/4: High-Level Assembly...", msg.chat.id, sent_msg.message_id, parse_mode="Markdown")
        img = cv2.bilateralFilter(img, 7, 50, 50)
        cv2.imwrite("temp_engine.jpg", img)

        # STAGE 4: Final Touchup (Pillow)
        bot.edit_message_text("🛠 *Processing...*\nStage 4/4: Final Polish & Touchup...", msg.chat.id, sent_msg.message_id, parse_mode="Markdown")
        final = Image.open("temp_engine.jpg")
        final = ImageEnhance.Sharpness(final).enhance(2.8)
        final = ImageEnhance.Contrast(final).enhance(1.1)
        final.save("output.jpg", quality=100, subsampling=0)

        with open("output.jpg", "rb") as f:
            bot.send_photo(msg.chat.id, f, caption="✅ *Enhanced via Multi-Stage Analysis*")
        
        bot.delete_message(msg.chat.id, sent_msg.message_id)
        
        # Cleanup (To keep Hosting clean)
        for f in ["raw.jpg", "temp_engine.jpg", "output.jpg"]:
            if os.path.exists(f): os.remove(f)
            
    except Exception as e:
        bot.send_message(msg.chat.id, "❌ Logic Error: Server Load or Image Issue.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True)
