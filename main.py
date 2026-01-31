import telebot
import replicate
import cv2
import numpy as np
import os
import requests
from PIL import Image, ImageEnhance, ImageFilter
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = "8416936551:AAFmNH1lpMv7md0GW9FkSWIarPo-dQsZmmw"
# Yahan apni Replicate API Key paste karein
os.environ["REPLICATE_API_TOKEN"] = "PASTE_YOUR_REPLICATE_KEY_HERE"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "iPhone AI Bot is running"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- IPHONE VIVID & TEXTURE FILTER (OpenCV) ---
def apply_iphone_vivid(img_path):
    img = cv2.imread(img_path)
    
    # 1. Saturation badhana (Vivid Look)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype("float32")
    hsv[:, :, 1] *= 1.25  # 25% extra saturation
    hsv = np.clip(hsv, 0, 255).astype("uint8")
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    cv2.imwrite("temp_vivid.jpg", img)
    return "temp_vivid.jpg"

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "✨ *iPhone AI Editor Ready!*\n\nBhejiye apni photo, main use:\n✅ OpenCV Vivid Filter\n✅ AI 4K Upscale\n✅ High Texture Skin\n\nmein badal dunga!", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def photo(msg):
    try:
        status_msg = bot.reply_to(msg, "🪄 Processing... iPhone Filters + AI 4K Scaling apply ho raha hai.")
        
        # Photo download karna
        file_id = msg.photo[-1].file_id
        file_info = bot.get_file(file_id)
        photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        # --- STEP 1: AI 4K Upscale (Replicate) ---
        # Ye background mein photo ko 4x bada aur clean karega
        output_url = replicate.run(
            "nightmare-ai/real-esrgan:42fed1c4974cc6b73a469f3c1212903333333333",
            input={
                "image": photo_url,
                "upscale": 4, 
                "face_enhance": True
            }
        )

        # AI processed photo download karna filter ke liye
        processed_data = requests.get(output_url).content
        with open("ai_out.jpg", "wb") as f:
            f.write(processed_data)

        # --- STEP 2: OpenCV iPhone Vivid Filter ---
        vivid_path = apply_iphone_vivid("ai_out.jpg")

        # --- STEP 3: Pillow Texture & Sharpness Enhancement ---
        img = Image.open(vivid_path)
        img = ImageEnhance.Sharpness(img).enhance(2.0) # Texture pop-up
        img = ImageEnhance.Contrast(img).enhance(1.1)
        img.save("final_output.jpg", quality=100, subsampling=0)

        # User ko final photo bhejna
        with open("final_output.jpg", "rb") as f:
            bot.send_photo(msg.chat.id, f, caption="🚀 *4K Ultra HD + iPhone Vivid Applied!*")

        # Cleanup
        bot.delete_message(msg.chat.id, status_msg.message_id)
        for f in ["ai_out.jpg", "temp_vivid.jpg", "final_output.jpg"]:
            if os.path.exists(f): os.remove(f)

    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(msg.chat.id, "Sorry, AI processing mein error aaya. API key check karein.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True)
