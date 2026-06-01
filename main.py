import os
import io
import telebot
from threading import Thread
from flask import Flask
import cv2
import numpy as np
from PIL import Image

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
        
        # GitHub ላይ የጫንከውን ባዶ የ Template B ጀርባ ምስል ማንበብ
        img_b = cv2.imread("template_b.jpg")
        if img_b is None:
            print("ስህተት፦ template_b.jpg ፋይል በGitHub ላይ አልተገኘም!")
            return None
        
        # መጠኖችን ለስራ እንዲመች አስተካክል
        img_a = cv2.resize(img_a, (1000, 1500))
        img_b = cv2.resize(img_b, (1200, 700))
        
        # --- ቁጥር 1፦ የፊት ፎቶን መቁረጥ እና ማሳረፍ ---
        face_crop = img_a[300:750, 320:800]
        face_resized = cv2.resize(face_crop, (315, 410)) # በሳጥን 1 ልክ
        img_b[180:590, 130:445] = face_resized
        
        # --- ቁጥር 2፦ ስም (አማርኛ እና እንግሊዝኛ) ---
        name_crop = img_a[900:1020, 150:700]
        name_resized = cv2.resize(name_crop, (320, 80)) # በሳጥን 2 ልክ
        img_b[290:370, 490:810] = name_resized
        
        # --- ቁጥር 3፦ የትውልድ ዘመን ---
        dob_crop = img_a[1030:1090, 150:700]
        dob_resized = cv2.resize(dob_crop, (320, 45)) # በሳጥን 3 ልክ
        img_b[455:500, 490:810] = dob_resized
        
        # --- ቁጥር 4፦ ጾታ (Sex) ---
        gender_crop = img_a[1095:1145, 150:400]
        gender_resized = cv2.resize(gender_crop, (320, 40)) # በሳጥን 4 ልክ
        img_b[565:605, 490:810] = gender_resized
        
        # --- ቁጥር 5፦ የሚያበቃበት ቀን (Expiry Date) ---
        exp_crop = img_a[1150:1210, 150:700]
        exp_resized = cv2.resize(exp_crop, (320, 45)) # በሳጥን 5 ልክ
        img_b[670:715, 490:810] = exp_resized
        
        # --- ቁጥር 6፦ የ FAN የባርኮድ ቁጥር ---
        barcode_crop = img_a[1215:1330, 300:750]
        barcode_resized = cv2.resize(barcode_crop, (280, 95)) # በሳጥን 6 ልክ
        img_b[765:860, 550:830] = barcode_resized
        
        # --- ቁጥር 7፦ በጎን በኩል ያለውን የቅጥያ ቀን ማዞር ---
        date_side_crop = img_a[330:1100, 880:960]
        date_rotated = cv2.rotate(date_side_crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
        date_side_resized = cv2.resize(date_rotated, (550, 45)) # በሳጥን 7 ልክ
        img_b[70:115, 100:650] = date_side_resized
        
        # ወደ PIL Image መቀየር
        final_preview = Image.fromarray(cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB))
        return final_preview
        
    except Exception as e:
        print(f"የምስል ሂደት ስህተት፦ {e}")
        return None

# 4. የቦቱ መልዕክት መቀበያ
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
            bot.send_message(chat_id, "❌ ይቅርታ፣ መታወቂያውን መቀየር አልተቻለም። template_b.jpg ፋይል በGitHub ላይ በትክክል መጫኑን ያረጋግጡ።")
            
        if os.path.exists(input_filename):
            os.remove(input_filename)
            
    except Exception as e:
        print(f"ስህተት፦ {e}")
        bot.send_message(message.chat.id, "❌ ስህተት አጋጥሟል።")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም! የ Template A ዲጂታል መታወቂያ ፎቶ ይላኩና ወደ Template B ቀይሬ እሰጥዎታለሁ።")

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()

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
