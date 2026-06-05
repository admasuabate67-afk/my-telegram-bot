import os
import cv2
import numpy as np
import easyocr
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. የቦት ቶከንዎን እዚህ ያስገቡ
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

# OCR አንባቢን ማዘጋጀት (አማርኛ እና እንግሊዝኛ ለማንበብ)
reader = easyocr.Reader(['am', 'en'])

# የዶክመንት መረጃዎችን እና ፎቶዎችን ከ Template A ላይ የመቁረጫ ቦታዎች (Coordinates)
# ማሳሰቢያ፦ እነዚህ ቁጥሮች እንደ ምስሉ ጥራት እና መጠን (Size) ሊቀያየሩ ስለሚችሉ እንደ አስፈላጊነቱ ያስተካክሏቸው።
COORDINATES_A = {
    "photo": (330, 310, 780, 590),       # [ymin, xmin, ymax, xmax] - ዋናው ፎቶ (1)
    "name": (610, 200, 660, 680),        # ስም (2)
    "dob": (675, 200, 715, 680),         # የትውልድ ቀን (3)
    "sex": (725, 200, 765, 680),         # ጾታ (4)
    "expiry": (775, 200, 815, 680),      # የሚያበቃበት ቀን (5)
    "card_num": (825, 330, 875, 680),    # ካርድ ቁጥር (6)
    "issue_date": (330, 900, 780, 950),   # የተሰጠበት ቀን (7) - በቁም የተጻፈው
}

# በ Template B ላይ መረጃዎቹ የሚያርፉባቸው ቦታዎች
COORDINATES_B = {
    "photo": (260, 130),       # (x, y) ለዋናው ፎቶ (1)
    "name": (410, 300),        # (x, y) ለስም (2)
    "dob": (410, 460),         # (x, y) ለትውልድ ቀን (3)
    "sex": (410, 560),         # (x, y) ለጾታ (4)
    "expiry": (410, 670),      # (x, y) ለማለፊያ ቀን (5)
    "card_num": (460, 570),    # (x, y) ለካርድ ቁጥር (6)
    "issue_date": (90, 85),    # (x, y) ለተሰጠበት ቀን (7)
    "small_photo": (740, 720)  # (x, y) ለትንሿ ፎቶ (8) - ከፋይዳ ጽሑፍ በታች
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 እንኳን ደህና መጡ! እባክዎን የ Template A መታወቂያ ፎቶ ይላኩልኝ።")

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ ምስሉን እያቀነባበርኩ ነው... እባክዎን በትዕግስት ይጠብቁ።")
    
    # ፎቶውን ማውረድ
    photo_file = await update.message.photo[-1].get_file()
    input_path = "template_a_input.jpg"
    await photo_file.download_to_drive(input_path)
    
    try:
        # Template B ባዶ ምስል መኖሩን ማረጋገጥ (ይህ ምስል በፎልደሩ ውስጥ መኖር አለበት)
        template_b_path = "template_b.jpg"
        if not os.path.exists(template_b_path):
            await update.message.reply_text("❌ ስህተት፡ 'template_b.jpg' የተባለው ባዶ ፋይል ሰርቨሩ ላይ አልተገኘም።")
            return

        # ምስሎችን በ OpenCV ማንበብ
        img_a = cv2.imread(input_path)
        img_b = cv2.imread(template_b_path)
        
        # 1. ፎቶዎችን መቁረጥ (Crop ዋናው ፎቶ እና ትንሿ ፎቶ)
        # ዋናው ፎቶ (1)
        y1, x1, y2, x2 = COORDINATES_A["photo"]
        main_photo = img_a[y1:y2, x1:x2]
        
        # ለቁጥር 8 የሚሆነውን ትንሿን ፎቶ ማዘጋጀት (የዋናው ፎቶ መጠን አሳንሶ መጠቀም ይቻላል)
        small_photo = cv2.resize(main_photo, (100, 130)) 
        
        # የተሰጠበት ቀን (7) በቁም ያለውን መቁረጥ
        y1_i, x1_i, y2_i, x2_i = COORDINATES_A["issue_date"]
        issue_date_crop = img_a[y1_i:y2_i, x1_i:x2_i]

        # 2. መረጃዎቹን በ OCR ማንበብ (ጽሑፎቹን ለይቶ ለማውጣት)
        # (ማሳሰቢያ፡ ይህ ለሙከራ ነው፤ ይበልጥ ትክክለኛ እንዲሆን ጽሑፍ ከመጻፍ ይልቅ የጽሑፍ ምስሉን ቆርጦ Template B ላይ መለጠፍ ይሻላል።)
        
        # 3. የተቆረጡትን ምስሎች ወደ Template B ላይ መለጠፍ
        # ዋናው ፎቶን መለጠፍ
        h, w, _ = main_photo.shape
        xb, yb = COORDINATES_B["photo"]
        img_b[yb:yb+h, xb:xb+w] = cv2.resize(main_photo, (w, h))
        
        # ቁጥር 8 (ትንሿን ፎቶ) መለጠፍ
        sh, sw, _ = small_photo.shape
        sxb, syb = COORDINATES_B["small_photo"]
        img_b[syb:syb+sh, sxb:sxb+sw] = small_photo

        # ቁጥር 7 (የተሰጠበት ቀን ምስል) መለጠፍ
        ih, iw, _ = issue_date_crop.shape
        ixb, iyb = COORDINATES_B["issue_date"]
        img_b[iyb:iyb+ih, ixb:ixb+iw] = issue_date_crop

        # ሌሎቹንም ክፍሎች (ስም፣ ጾታ፣ ወዘተ) በተመሳሳይ መልኩ ከ Template A ቆርጦ Template B ላይ መለጠፍ ይቻላል፡
        for key in ["name", "dob", "sex", "expiry", "card_num"]:
            y1, x1, y2, x2 = COORDINATES_A[key]
            text_crop = img_a[y1:y2, x1:x2]
            th, tw, _ = text_crop.shape
            xb, yb = COORDINATES_B[key]
            # Template B ላይ ቦታው እንዲበቃው መጠኑን ማስተካከል
            img_b[yb:yb+th, xb:xb+tw] = text_crop

        # የተዘጋጀውን አዲስ ምስል ሴቭ ማድረግ
        output_path = "output_template_b.jpg"
        cv2.imwrite(output_path, img_b)
        
        # ውጤቱን ለተጠቃሚው መላክ
        await update.message.reply_photo(photo=open(output_path, 'rb'), caption="✅ መረጃው በTemplate B ላይ በትክክል ተስተካክሏል!")
        
        # ጊዜያዊ ፋይሎችን ማጽዳት
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        await update.message.reply_text(f"❌ ምስሉን በማቀናበር ላይ ስህተት አጋጥሟል፡ {str(e)}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, process_image))
    print("ቦቱ ስራ ጀምሯል...")
    application.run_polling()

if __name__ == "__main__":
    main()
