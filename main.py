import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)
from PIL import Image

# በምስሉ ላይ የሚታየው ትክክለኛው እና የነቃው ቦት ቶክን
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
    # 1. የተላከውን የTemplate A ምስል ማውረድ
    photo_file = await update.message.photo[-1].get_file()
    template_a_path = f"template_a_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(template_a_path)
    
    await update.message.reply_text("⏳ ምስሉ ደርሷል! መረጃዎችን በትክክል እየቆረጥኩ እና እያቀናጀሁ ነው፣ እባክዎ በትዕግስት ይጠብቁ...")
    
    try:
        # 2. ባዶውን Template B መክፈት
        template_b_path = "template_b.jpg"
        if not os.path.exists(template_b_path):
            # ፋይሉ ከሌለ ለሙከራ ያህል ባለ 1000x600 ምስል ይፈጥራል
            template_b = Image.new("RGB", (1034, 574), "white")
        else:
            template_b = Image.open(template_b_path)
            
        # 3. ዋናውን Template A ምስል መክፈት
        img_a = Image.open(template_a_path)
        
        # ⚠️ ዋና ማሳሰቢያ፦ ሁሉም መታወቂያዎች በእኩል ሳይዝ እንዲቆረጡ መጀመሪያ የተላከውን ምስል ስታንዳርድ ሳይዝ እናደርገዋለን
        # ይህ ምስሉ ከስልኩ ስክሪንሾት ጥራት ጋር እንዳይቀያየር ይረዳል
        img_a = img_a.resize((1000, 1500)) 

        # 4. ✂️ መረጃዎቹን ከ Template A ላይ በ Box (Left, Upper, Right, Lower) መቁረጥ
        # (እነዚህን ቁጥሮች ያንተ መታወቂያ ፎቶ ላይ ባለው አቀማመጥ ልክ ወደ ግራ/ቀኝ/ላይ/ታች ፈቀቅ ማድረግ ትችላለህ)
        
        # ቁጥር 1፦ ፎቶግራፍ
        crop_1 = img_a.crop((330, 290, 780, 850))
        crop_1_resized = crop_1.resize((270, 360))
        template_b.paste(crop_1_resized, (135, 130))
        
        # ቁጥር 2፦ ሙሉ ስም
        crop_2 = img_a.crop((170, 920, 680, 1020))
        crop_2_resized = crop_2.resize((290, 60))
        template_b.paste(crop_2_resized, (420, 145))
        
        # ቁጥር 3፦ የትውልድ ቀን
        crop_3 = img_a.crop((170, 1060, 680, 1120))
        crop_3_resized = crop_3.resize((290, 40))
        template_b.paste(crop_3_resized, (420, 245))
        
        # ቁጥር 4፦ ጾታ
        crop_4 = img_a.crop((170, 1140, 450, 1200))
        crop_4_resized = crop_4.resize((200, 40))
        template_b.paste(crop_4_resized, (420, 320))
        
        # ቁጥር 5፦ የሚያበቃበት ቀን
        crop_5 = img_a.crop((170, 1220, 680, 1280))
        crop_5_resized = crop_5.resize((290, 40))
        template_b.paste(crop_5_resized, (420, 395))
        
        # ቁጥር 6፦ የካርድ ቁጥር FAN
        crop_6 = img_a.crop((330, 1310, 730, 1420))
        crop_6_resized = crop_6.resize((250, 65))
        template_b.paste(crop_6_resized, (470, 480))
        
        # ቁጥር 7፦ የተሰጠበት ቀን (በቁም የተጻፈው)
        crop_7 = img_a.crop((910, 350, 960, 1000))
        # ይህንን ጽሑፍ በቁምነቱ ለማቆየት ማሽከርከር ካስፈለገ .rotate(90, expand=True) መጠቀም ይቻላል
        crop_7_resized = crop_7.resize((35, 330))
        template_b.paste(crop_7_resized, (75, 140))

        # ቁጥር 8፦ 🖼 ሙሉውን የTemplate A ምስል አሳንሶ "ፋይዳ" ከሚለው በታች መለጠፍ
        crop_8_resized = img_a.resize((85, 110))
        template_b.paste(crop_8_resized, (765, 415))

        # 5. የተሰራውን የመጨረሻ መታወቂያ ሴቭ አድርጎ ለተጠቃሚው መላክ
        output_file = f"final_id_{update.message.from_user.id}.jpg"
        template_b.save(output_file)
        
        await update.message.reply_photo(
            photo=open(output_file, 'rb'),
            caption="🎉 መታወቂያው ከ Template A ላይ መረጃዎቹ በትክክል ተቆርጠው ወደ Template B ተዛውረዋል!"
        )
        
        # ጊዜያዊ ፋይሎችን ከሰርቨሩ ላይ ማጽዳት
        if os.path.exists(template_a_path): os.remove(template_a_path)
        if os.path.exists(output_file): os.remove(output_file)

    except Exception as e:
        await update.message.reply_text(f"ይቅርታ፣ ምስሉን በመቁረጥ ላይ ስህተት አጋጥሟል፦ {str(e)}")
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
