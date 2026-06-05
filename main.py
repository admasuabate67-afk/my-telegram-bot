import os
import re
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
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

TOKEN = "8941497236:AAE-Cl4FeJc9nQEZ6tugHRUmIABhLCsptdA"

app = Flask(__name__)

@app.route('/')
def home():
    return "Fayda PDF Converter Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context):
    await update.message.reply_text(
        "ሰላም! እንኳን ወደ ፋይዳ ፒዲኤፍ መለወጫ ቦት በሰላም መጡ። 🎉\n\n"
        "እባክዎ መረጃው እንዲቀየር የፈለጉትን ኦሪጅናል **የፋይዳ PDF ፋይል** ይላኩልኝ።"
    )

async def process_pdf_conversion(update: Update, context):
    # 1. የተላከውን የPDF ፋይል ማውረድ
    pdf_document = update.message.document
    if not pdf_document.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("እባክዎ ትክክለኛ የ PDF ፋይል ብቻ ይላኩ!")
        return

    pdf_path = f"fayda_{update.message.from_user.id}.pdf"
    file_info = await context.bot.get_file(pdf_document.file_id)
    await file_info.download_to_drive(pdf_path)
    
    await update.message.reply_text("⏳ የፋይዳ PDF ፋይል ደርሷል! መረጃዎችን እና ፎቶዎችን ያለስህተት እያወጣሁ ነው...")
    
    try:
        # 2. ከPDF ጽሑፎችን በራስ-ሰር ማንበብ (TEXT EXTRACTION)
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        # በመደበኛ መግለጫዎች (Regex) መረጃዎቹን መለየት
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        # ስም ፍለጋ (ከ Admasu Abate Dinbale አይነት አወቃቀር ጋር የተገጣጠመ)
        name_en = "ያልተገኘ"
        name_am = "ያልተገኘ"
        for i, line in enumerate(lines):
            if "Ethiopian Digital ID Card" in line or "FAYDA DIGITAL COPY" in line:
                if i + 1 < len(lines):
                    name_am = lines[i+1]
                if i + 2 < len(lines):
                    name_en = lines[i+2]
                break

        # ቀናትን እና ቁጥሮችን መለየት
        dates = re.findall(r'(\d{2}/\d{2}/\d{4})', full_text) # የትውልድ ቀን
        fan_match = re.search(r'FAN\s*(\d{16})|(\d{16})', full_text) # 16 ዲጂት የካርድ ቁጥር
        
        dob = dates[0] if len(dates) > 0 else "ያልተገኘ"
        issue_date = dates[1] if len(dates) > 1 else "ያልተገኘ"
        exp_date = dates[2] if len(dates) > 2 else "ያልተገኘ"
        card_num = fan_match.group(0).replace("FAN", "").strip() if fan_match else "ያልተገኘ"
        gender = "ወንድ / Male" if "ወንድ" in full_text or "Male" in full_text else "ሴት / Female"

        # 3. 📸 ፎቶውን ከPDF ገጽ ላይ ቆርጦ ማውጣት
        # PDF ገጹን ወደ ምስል እንቀይረዋለን (የመጀመሪያውን ገጽ)
        images = convert_from_path(pdf_path, dpi=200)
        pdf_page_img = images[0]
        # በኦሪጅናሉ ፒዲኤፍ አቀማመጥ ልክ የባለቤቱን ፎቶ ብቻ መቁረጥ (የፎቶው መጋጠሚያ)
        pdf_page_img_resized = pdf_page_img.resize((1600, 2200))
        extracted_user_photo = pdf_page_img_resized.crop((120, 580, 480, 1020)) # የፎቶ መገኛ ሳጥን
        
        # 4. 🖼 አዲሱን Template B ምስል ማዘጋጀት
        template_b_path = "template_b.jpg"
        if not os.path.exists(template_b_path):
            template_b = Image.new("RGB", (1034, 574), "white")
        else:
            template_b = Image.open(template_b_path)
            
        draw = ImageDraw.Draw(template_b)
        
        # የአማርኛ ፎንት (nyala.ttf በፎልደሩ ውስጥ መኖር አለበት)
        font_path = "nyala.ttf"
        font = ImageFont.truetype(font_path, 22) if os.path.exists(font_path) else ImageFont.load_default()
        font_side = ImageFont.truetype(font_path, 18) if os.path.exists(font_path) else ImageFont.load_default()

        # 5. ✍️ መረጃዎቹን Template B ላይ በትክክለኛው ቦታቸው መጻፍ
        draw.text((415, 140), f"{name_am}\n{name_en}", fill="black", font=font) # ቁጥር 2 (ስም)
        draw.text((415, 245), f"{dob}", fill="black", font=font)               # ቁጥር 3 (ትውልድ ቀን)
        draw.text((415, 320), f"{gender}", fill="black", font=font)            # ቁጥር 4 (ጾታ)
        draw.text((415, 395), f"{exp_date}", fill="black", font=font)          # ቁጥር 5 (የሚያበቃበት ቀን)
        draw.text((460, 485), f"{card_num}", fill="black", font=font)          # ቁጥር 6 (የካርድ ቁጥር)
        
        # ለቁጥር 7 (በቁም የተሰጠበት ቀን)
        draw.text((75, 145), f"{issue_date}", fill="black", font=font_side)

        # 6. 🖼 የተቆረጠውን ፎቶ (ቁጥር 1) በቦታው መለጠፍ
        user_photo_resized = extracted_user_photo.resize((265, 345))
        template_b.paste(user_photo_resized, (138, 132))

        # 7. 🖼 ለቁጥር 8 (ሙሉውን የፒዲኤፍ ገጽ ምስል በትንሹ አሳንሶ መለጠፍ)
        mini_pdf_page = pdf_page_img.resize((85, 110))
        template_b.paste(mini_pdf_page, (768, 418))

        # 8. የተሰራውን የመጨረሻ ምስል ሴቭ አድርጎ ለተጠቃሚው መላክ
        output_file = f"final_id_from_pdf_{update.message.from_user.id}.jpg"
        template_b.save(output_file)
        
        await update.message.reply_photo(
            photo=open(output_file, 'rb'),
            caption="🎉 መታወቂያው ከፋይዳ PDF ፋይል ላይ በራስ-ሰር ተለቅሞ በ Template B ላይ በከፍተኛ ጥራት ተዘጋጅቷል!"
        )
        
        # ጊዜያዊ ፋይሎችን ማጽዳት
        if os.path.exists(pdf_path): os.remove(pdf_path)
        if os.path.exists(output_file): os.remove(output_file)

    except Exception as e:
        await update.message.reply_text(f"ይቅርታ፣ ከ PDF ላይ መረጃ በማውጣት ላይ ስህተት አጋጥሟል፦ {str(e)}")
        if os.path.exists(pdf_path): os.remove(pdf_path)

def main():
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    # ተጠቃሚው ፋይል/ዶክመንት ሲልክ ይህንን ፋንክሽን እንዲያነቃው ማድረግ
    application.add_handler(MessageHandler(filters.Document.ALL, process_pdf_conversion))
    
    application.run_polling()

}
if __name__ == "__main__":
    main()
