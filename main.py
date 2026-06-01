import os
import io
import telebot
from threading import Thread
from flask import Flask, send_from_directory, safe_join
import easyocr
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 1. ያመጣኸው ትክክለኛ የቦት ቶክን እዚህ ገብቷል (አሁንም ቶክኑን በ Environment Variable መተካት ይመከራል)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8941497236:AAGMV8X7GYytc2Iv2DHIQUMIogrHh1vzBGE')
bot = telebot.TeleBot(BOT_TOKEN)

# 2. ለ Render የሚሆን ቀላል የ Flask ዌብ ሰርቨር መፍጠር
app = Flask(__name__)
# ፎንት ፋይሎችን ለማገልገል static directory ፍጠር
app.static_folder = 'static'

@app.route('/')
def home():
    return "ቦቱ በሰላም እየሰራ ነው! (መታወቂያ ቀያሪ)"

@app.route('/font/<filename>')
def serve_font(filename):
    return send_from_directory(app.static_folder, filename)

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. OCR እና Image Processing ተግባራት

# OCR Reader ለ አማርኛ እና እንግሊዝኛ
reader = easyocr.Reader(['am', 'en'])

# የአማርኛ ፎንት ፋይል (በፕሮጀክቱ root ውስጥ መኖር አለበት)
FONT_FILE_AMH = "NotoSansEthiopic-Regular.ttf"
FONT_SIZE = 18

def get_text_from_region(image, region):
    x, y, w, h = region
    cropped_img = image[y:y+h, x:x+w]
    # OCR ን አንብብ
    result = reader.readtext(cropped_img)
    # ሁሉንም የተነበቡ ጽሑፎች በአንድነት ሰብስብ
    text = " ".join([res[1] for res in result])
    return text.strip()

def extract_face(image):
    # የፊት መለየትን ለማከናወን የ OpenCV ቀላሉን የፊት መቁረጫ እንጠቀማለን
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        return None
    
    # የመጀመሪያውን ፊት ቆርጠህ
    for (x,y,w,h) in faces:
        cropped_face = image[y:y+h, x:x+w]
        return cropped_face

def convert_id(photo_path):
    # የገባውን መታወቂያ ፎቶ ጫን
    img_a_cv = cv2.imread(photo_path)
    if img_a_cv is None:
        return None

    # የOCR እና የፊት መቁረጥን ለማከናወን የስራ ሂደቶችን ፍጠር
    # (በ'Template A' ላይ ያሉትን የተወሰኑ ቦታዎች መወሰን ያስፈልጋል - ይህ በጣም ውስብስብ ነው)
    # ለምሳሌ፡ የሳጥን 1, 2, 3, ወዘተ መገኛ ቦታዎችን አስቀድሞ መወሰን

    # (ይህንን ክፍል በተሻለ ሁኔታ ለማሳካት የ'Template A'ን የተወሰኑ የ座標 (coordinates) መወሰን ያስፈልጋል)
    # ለምሳሌ፡
    region_name_am = (x1, y1, w1, h1) # የሳጥን 2 የላይኛው ክፍል (አማርኛ ስም)
    region_name_en = (x2, y2, w2, h2) # የሳጥን 2 የታችኛው ክፍል (እንግሊዝኛ ስም)
    # ወዘተ ለሌሎች ሳጥኖች (3፣ 4፣ 5፣ 6)

    # ጽሑፎችን አንብብ
    # name_am = get_text_from_region(img_a_cv, region_name_am)
    # name_en = get_text_from_region(img_a_cv, region_name_en)
    # date_birth = get_text_from_region(img_a_cv, region_dob)
    # sex = get_text_from_region(img_a_cv, region_sex)
    # fan = get_text_from_region(img_a_cv, region_fan)

    # (ለአሁኑ OCR ን ለመተው እና ወደ'Template B' ለመቀየር፣ ፊቱን ብቻ ቆርጠን እንለጥፍ)
    
    # ፊቱን ቁረጥ
    face_img_cv = extract_face(img_a_cv)

    # ባዶውን'Template B' ምስል ጫን (ይህ በፕሮጀክቱ root ውስጥ መኖር አለበት)
    template_b_cv = cv2.imread("template_b_blank.jpg")
    if template_b_cv is None:
        # ለተጠቃሚው መልዕክት ለመላክ ፋይሉ እንደሌለ አሳይ
        return None

    # የተቆረጠውን ፊት በ'Template B' ላይ ለጥፍ (በሳጥን 1 ቦታ)
    if face_img_cv is not None:
        face_img_pil = Image.fromarray(cv2.cvtColor(face_img_cv, cv2.COLOR_BGR2RGB))
        # ፊቱን በትክክለኛው መጠን ቀይር (የሳጥን 1 መጠን)
        face_img_pil = face_img_pil.resize((x_scale, y_scale))
        
        template_b_pil = Image.fromarray(cv2.cvtColor(template_b_cv, cv2.COLOR_BGR2RGB))
        template_b_pil.paste(face_img_pil, (x_face, y_face)) # የሳጥን 1 መገኛ
        
        # ወደ OpenCV ተመለስ
        template_b_cv = cv2.cvtColor(np.array(template_b_pil), cv2.COLOR_RGB2BGR)

    # (ጽሑፎችን ለመጻፍ Pillow ን መጠቀም - ይህ የአማርኛ ፎንቶችን በትክክል ለመጻፍ ያስችላል)
    # name_pil = Image.fromarray(cv2.cvtColor(template_b_cv, cv2.COLOR_BGR2RGB))
    # draw = ImageDraw.Draw(name_pil)
    
    # ፎንቱን ጫን (NotoSansEthiopic)
    # font_am = ImageFont.truetype(FONT_FILE_AMH, FONT_SIZE)
    # font_en = ImageFont.truetype("arial.ttf", FONT_SIZE)

    # የአማርኛ ጽሑፍን በ draw.text((x, y), name_am, font=font_am, fill=(0, 0, 0)) መጻፍ

    # (ለአሁኑ፣ ፊቱን ብቻ የለጠፈውን ምስል እንላክ)
    
    return template_b_cv

# 4. የቦቱ Handler (photo_handler)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, "መታወቂያውን በመቀየር ላይ ነው፣ እባክዎ ይጠብቁ...")

        # ፎቶውን ከቴሌግራም አውርድ
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # ለጊዜው አስቀምጥ
        photo_path = f"id_photo_{chat_id}.jpg"
        with open(photo_path, 'wb') as f:
            f.write(downloaded_file)

        # መታወቂያውን ቀይር
        converted_img_cv = convert_id(photo_path)

        if converted_img_cv is not None:
            # የተለወጠውን ምስል ወደ ቴሌግራም መላክ (እንደ io.BytesIO)
            # ፊቱን ብቻ የመለጠፍ ውጤት ለመላክ
            converted_img_pil = Image.fromarray(cv2.cvtColor(converted_img_cv, cv2.COLOR_BGR2RGB))
            bio = io.BytesIO()
            converted_img_pil.save(bio, format='JPEG')
            bio.seek(0)
            bot.send_photo(chat_id, bio, caption="የተቀየረው'Template B' መታወቂያዎ (ሙከራ)")
        else:
            bot.send_message(chat_id, "ይቅርታ፣ መታወቂያውን መቀየር አልተቻለም። ባዶ የ'Template B' ፋይል መኖሩን ያረጋግጡ።")

        # ለጊዜው የተቀመጡትን ፋይሎች አጥፋ
        os.remove(photo_path)

    except Exception as e:
        print(f"Error handling photo: {e}")
        bot.send_message(message.chat.id, "ይቅርታ፣ ያልተጠበቀ ስህተት አጋጥሟል።")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "እንኳን ደህና መጡ! ቦቱ በሰላም እየሰራ ነው። ለመታወቂያ መቀየር፣ የ'Template A' መታወቂያዎን በፎቶ መልክ ይላኩ።")

# 5. ቦቱ እና ዌብ ሰርቨሩ በአንድ ላይ እንዲሰሩ ማድረግ
if __name__ == "__main__":
    # የ Flask ሰርቨሩን ከበስተጀርባ (Background Thread) ማስነሳት
    t = Thread(target=run_flask)
    t.start()
    
    print("ቦቱ እየጀመረ ነው...")
    # ቦቱ መልዕክቶችን ሳያቋርጥ እንዲቀበል ማድረግ
    bot.infinity_polling()
