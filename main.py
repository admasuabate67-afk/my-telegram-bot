import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters
)
from PIL import Image

# ትክክለኛው የቦት ቶከን
TOKEN = "8941497236:AAE-Cl4FeJc9nQEZ6tugHRUmIABhLCsptdA"

app = Flask(__name__)

@app.route('/')
def home():
    return "Template Crop Converter is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context):
    await update.message.reply_text(
        "ሰላም! እንኳን ወደ መታወቂያ ማቀናበሪያ ቦት በሰላም መጡ።\n\n"
        "እባክዎ የተጠቃሚውን **የTemplate A መታወቂያ ፎቶ (Screenshot)** ይላኩ።"
    )

async def process_image_conversion(update: Update, context):
    photo_file = await update.message.photo[-1].get_file()
    template_a_path = f"template_a_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(template_a_path)
    
    await update.message.reply_text("⏳ ምስሉ ደርሷል! መረጃዎችን በትክክል እየቆረጥኩ እና እያቀናጀሁ ነው፣ እባክዎ በትዕግስት ይጠብቁ...")
    
    try:
        # 1. ባዶውን Template B መክፈት
        template_b_path = "template_b.jpg"
        if not os.path.exists(template_b_path):
            # ባዶ ምስል ፈጣሪ (ፋይሉ ከጠፋ)
            template_b = Image.new("RGB", (1034, 574), "white")
        else:
            template_b = Image.open(template_b_path)
            
        # 2. ዋናውን Template A ምስል መክፈት
        img_a = Image.open(template_a_path)
        
        # ስክሪንሾቱ ምንም ዓይነት መጠን ቢኖረው መጀመሪያ ወደ አንድ ወጥ ስታንዳርድ መጠን እንቀይረዋለን
        img_a = img_a.resize((1000, 1500)) 

        # 3. ✂️ የተስተካከሉ የቁረጥ እና የመለጠፍ መጋጠሚያዎች (Coordinates)

        # 1️⃣ ፎቶግራፍ (ቁጥር 1)
        crop_1 = img_a.crop((320, 270, 750, 830))
        crop_1_resized = crop_1.resize((265, 345))
        template_b.paste(crop_1_resized, (138, 132))
        
        # 2️⃣ ሙሉ ስም (ቁጥር 2)
        crop_2 = img_a.crop((160, 910, 720, 1010))
        crop_2_resized = crop_2.resize((480, 55))
        template_b.paste(crop_2_resized, (415, 145))
        
        # 3️⃣ የትውልድ ቀን (ቁጥር 3)
        crop_3 = img_a.crop((160, 1050, 720, 1115))
        crop_3_resized = crop_3.resize((480, 40))
        template_b.paste(crop_3_resized, (415, 245))
        
        # 4️⃣ ጾታ (ቁጥር 4)
        crop_4 = img_a.crop((160, 1130, 480, 1195))
        crop_4_resized = crop_4.resize((280, 40))
        template_b.paste(crop_4_resized, (415, 320))
        
        # 5️⃣ የሚያበቃበት ቀን (ቁጥር 5)
        crop_5 = img_a.crop((160, 1210, 720, 1275))
        crop_5_resized = crop_5.resize((480, 40))
        template_b.paste(crop_5_resized, (415, 395))
        
        # 6️⃣ የካርድ ቁጥር FAN (ቁጥር 6)
        crop_6 = img_a.crop((310, 1315, 750, 1415))
        crop_6_resized = crop_6.resize((350, 50))
        template_b.paste(crop_6_resized, (460, 485))
        
        # 7️⃣ የተሰጠበት ቀን (ቁጥር 7) -> 🔄 በ 90 ዲግሪ አዙሮ በቁም ለመለጠፍ
        crop_7 = img_a.crop((915, 350, 955, 950))
        crop_7_rotated = crop_7.rotate(90, expand=True) # ፅሁፉን በቁም ያዞረዋል
        crop_7_resized = crop_7.rotated.resize((35, 310)) if hasattr(crop_7_rotated, 'resize') else crop_7_rotated.resize((35, 310))
        # በግራ በኩል ባለው ጠባብ ሳጥን ውስጥ ማስገቢያ
        template_b.paste(crop_7_resized, (75, 145))

        # 8️⃣ የTemplate A ሙሉ ምስል በትንሹ (ቁጥር 8)
        crop_8_resized = img_a.resize((85, 110))
        template_b.paste(crop_8_resized, (768, 418))

        # 4. የመጨረሻውን ፋይል ሴቭ አድርጎ መላክ
        output_file = f"final_id_{update.message.from_user.id}.jpg"
        template_b.save(output_file)
        
        await update.message.reply_photo(
            photo=open(output_file, 'rb'),
            caption="🎉 መታወቂያው በ Template B ላይ ፍጹም በሆነ አቀማመጥ ተዘጋጅቷል!"
        )
        
        # ጊዜያዊ ፋይሎችን ማጽዳት
        if os.path.exists(template_a_path): os.remove(template_a_path)
        if os.path.exists(output_file): os.remove(output_file)

    except Exception as e:
        await update.message.reply_text(f"ይቅርታ፣ ምስሉን በማቀናጀት ላይ ስህተት አጋጥሟል፦ {str(e)}")
        if os.path.exists(template_a_path): os.remove(template_a_path)

def main():
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.PHOTO, process_image_conversion))
    
    application.run_polling()

if __name__ == "__main__":
    main()
