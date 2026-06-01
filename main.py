import os
import io
import telebot
from threading import Thread
from flask import Flask
import cv2
import numpy as np
from PIL import Image
import requests

# 1. የቦት ቶክን ማዋቀር
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8941497236:AAGMV8X7GYytc2Iv2DHIQUMIogrHh1vzBGE')
bot = telebot.TeleBot(BOT_TOKEN)

# 2. ለ Render የሚሆን የ Flask ዌብ ሰርቨር
app = Flask('')

@app.route('/')
def home():
    return "የመታወቂያ መቀየሪያ ቦቱ በሰላም እየሰራ ነው!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. ምስልን የመቁረጥ እና የማስተካከል ዋና ተግባር
def process_id_conversion(input_image_path):
    try:
        # Template A ፎቶን ማንበብ
        img_a = cv2.imread(input_image_path)
        if img_a is None:
            return None
        
        # የባዶውን Template B ምስል በቀጥታ ከሊንክ ማውረድ (የፋይል ስም ችግርን ለመፍታት)
        template_url = "https://raw.githubusercontent.com/admasuabate67-afk/my-telegram-bot/main/template_b.jpg"
        resp = requests.get(template_url, timeout=10)
        
        if resp.status_code == 200:
            image_bytes = np.asarray(bytearray(resp.content), dtype="uint8")
            img_b = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        else:
            img_b = cv2.imread("template_b.jpg")
            
        if img_b is None:
            print("ስህተት፦ Template B ጀርባ ምስል ሊነበብ አልቻለም!")
            return None
        
        # መጠኖችን ማስተካከል
        img_a = cv2.resize(img_a, (1000, 1500))
        img_b = cv2.resize(img_b, (1200, 700))
        
        # --- ሳጥን 1፦ የፊት ፎቶን መቁረጥ እና ማሳረፍ ---
        face_crop = img_a[300:750, 320:800]
        face_resized = cv2.resize(face_crop, (315, 410)) 
        img_b[180:590, 130:445] = face_resized
        
        # --- ሳጥን 2፦ ስም ---
        name_crop = img_a[900:1020, 150:700]
        name_resized = cv2.resize(name_crop, (320, 80)) 
        img_b[290:370, 490:810] = name_resized
        
        # --- ሳጥን 3፦ የትውልድ ዘመን ---
        dob_crop = img_a[1030:1090, 150:700]
        dob_resized = cv2.resize(dob_crop, (320, 45)) 
        img_b[455:500, 490:810] = dob_resized
        
        # --- ሳጥን 4፦ ጾታ ---
        gender_crop = img_a[1095:1145, 150:400]
        gender_resized = cv2.resize(gender_crop, (320, 40)) 
        img_b[565:605, 490:810] = gender_resized
        
        # --- ሳጥን 5፦ የሚያበቃበት ቀን ---
        exp_crop = img_a[1150:1210, 150:700]
        exp_resized = cv2.resize(exp_crop, (320, 45)) 
        img_b[670:715, 490:810] = exp_resized
        
        # --- ሳጥን 6፦ የ FAN የባርኮድ ቁጥር ---
        barcode_crop = img_a[1215:1330, 300:750]
        barcode_resized = cv2.resize(barcode_crop, (280, 95)) 
        img_b[765:860, 550:830] = barcode_resized
        
        # --- ሳጥን 7፦ በጎን በኩል ያለውን የቅጥያ ቀን ማዞር ---
        date_side_crop = img_a[330:1100, 880:960]
        date_rotated = cv2.rotate(date_side_crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
        date_side_resized = cv2.resize(date_rotated, (550, 45)) 
        img_b[70:115, 100:650] = date_side_resized
        
        final_preview = Image.fromarray(cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB))
        return final_preview
        
    except Exception as e:
        print(f"የምስል ሂደት ስህተት፦ {e}")
        return None

# 4. የቦቱ መልዕክት መቀበያ (Photo Handler)
@bot.message_handler(content_types=['photo'])
def handle_id_photo(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, "⏳ የTemplate A መታወቂያ መረጃዎችን ወደ Template B በመቀየር ላይ ነኝ... እባክዎ ይጠብቁ።")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_filename = f"input_{chat_id}.jpg"
        with open(input_filename, 'wb') as f:
            f.write(downloaded_file)
        
        output_image = process_id_conversion(input_filename)
        
        if output_image is not None:
            bio = io.BytesIO()
            output_image.save(bio, format='JPEG', quality=95)
            bio.seek(0)
            bot.send_photo(chat_id, bio, caption="✅ መታወቂያው በተሳካ ሁኔታ ወደ Template B ተቀይሯል!")
        else:
            bot.send_message(chat_id, "❌ ይቅርታ፣ መታወቂያውን መቀየር አልተቻለም። የTemplate B ፋይልን ማግኘት አልተቻለም።")
            
        if os.path.exists(input_filename):
            os.remove(input_filename)
            
    except Exception as e:
        print(f"ስህተት፦ {e}")
        bot.send_message(message.chat.id, "❌ የቴክኒክ ስህተት አጋጥሟል።")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም! የ Template A ዲጂታል መታወቂያ ፎቶ ይላኩና ወደ Template B ቀይሬ እሰጥዎታለሁ።")

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print("ቦቱ እየጀመረ ነው...")
    bot.infinity_polling()
