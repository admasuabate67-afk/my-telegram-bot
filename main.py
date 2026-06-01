import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. Render ሰርቨር እንዳይዘጋ (Web Server Dummy ሎጂክ)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is Running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"የዌብ ሰርቨር በፖርት {port} ላይ ተነስቷል...")
    server.serve_forever()

# 2. ቦቱ ሲነሳ የሚናገረው ሰላምታ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! እንኳን ወደ መታወቂያ መለወጫ (Convertor) ቦት በሰላም መጡ።\n"
        "እባክዎ ለመቀየር የሚፈልጉትን የቆየ መታወቂያ ፎቶ (Template A) ይላኩ።"
    )

# 3. ፎቶ ሲላክለት ቆርጦ Template B ላይ የሚለጥፈው ዋና ሎጂክ
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("መታወቂያው ደርሶኛል! መረጃዎችን ወደ አዲሱ Template በመቀየር ላይ ነው፣ እባክዎ ይጠብቁ...")
    
    input_path = f"user_{update.message.chat_id}.jpg"
    output_path = f"converted_{update.message.chat_id}.jpg"
    template_b_path = "template_b.jpg"
    
    try:
        if not os.path.exists(template_b_path):
            await update.message.reply_text("💡 ስህተት፡ template_b.jpg የተባለው ባዶ መታወቂያ GitHub ላይ አልተጫነም!")
            return
            
        img_a = Image.open(input_path).convert("RGBA")
        img_b = Image.open(template_b_path).convert("RGBA")
        
        img_a = img_a.resize((1200, 800))
        img_b = img_b.resize((1200, 800))
        
        # የፊት ፎቶ መቁረጫ
        photo_box = (650, 150, 900, 500)
        cropped_photo = img_a.crop(photo_box)
        img_b.paste(cropped_photo, (700, 150), cropped_photo)
        
        # የጽሑፍ መረጃ መቁረጫ
        info_box = (50, 180, 600, 450)
        cropped_info = img_a.crop(info_box)
        img_b.paste(cropped_info, (380, 220), cropped_info)
        
        final_img = img_b.convert("RGB")
        final_img.save(output_path, "JPEG")
        
        await update.message.reply_photo(
            photo=open(output_path, 'rb'), 
            caption="🎉 እንኳን ደስ አለዎት! መታወቂያዎ በተካ ሁኔታ ወደ አዲሱ ዲጂታል Template ተቀይሯል።"
        )
        
    except Exception as e:
        await update.message.reply_text(f"ማስተላለፍ አልተቻለም፣ ስህተት አጋጥሟል: {str(e)}")
        
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    TOKEN = "7917849176:AAH6YfXor3Vq27eQOfv6Rsc0H8m69RbyE1g"
    
    # የዌብ ሰርቨሩን በባክግራውንድ ማስነሳት (ለ Render ማታለያ)
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    app = Application.builder().token(TOKEN).read_timeout(30).connect_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("ቦቱ በስኬት ስራ ጀምሯል...")
    app.run_polling(allowed_updates=[Update.MESSAGE])

if __name__ == '__main__':
    main()
        
        # ሎጂክ 1፦ የግለሰቡን የፊት ፎቶ ቆርጦ አዲሱ ላይ መለጠፍ
        photo_box = (650, 150, 900, 500) # (left, upper, right, lower)
        cropped_photo = img_a.crop(photo_box)
        img_b.paste(cropped_photo, (700, 150), cropped_photo)
        
        # ሎጂክ 2፦ የጽሑፍ መረጃዎችን ቆርጦ ማስተላለፍ (ስም፣ ልደት)
        info_box = (50, 180, 600, 450) 
        cropped_info = img_a.crop(info_box)
        img_b.paste(cropped_info, (380, 220), cropped_info)
        
        # የመጨረሻውን ውጤት ሴヴ ማድረግ
        final_img = img_b.convert("RGB")
        final_img.save(output_path, "JPEG")
        
        # የተዘጋጀውን አዲሱን መታወቂያ መለስክ መላክ
        await update.message.reply_photo(
            photo=open(output_path, 'rb'), 
            caption="🎉 እንኳን ደስ አለዎት! መታወቂያዎ በተሳካ ሁኔታ ወደ አዲሱ ዲጂታል Template ተቀይሯል።"
        )
        
    except Exception as e:
        await update.message.reply_text(f"ማስተላለፍ አልተቻለም፣ ስህተት አጋጥሟል: {str(e)}")
        
    finally:
        # ጊዜያዊ ፋይሎችን ማጽዳት
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    # የአንተ ቦት ቶከን
    TOKEN = "7917849176:AAH6YfXor3Vq27eQOfv6Rsc0H8m69RbyE1g"
    
    app = Application.builder().token(TOKEN).read_timeout(30).connect_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("ቦቱ በስኬት ስራ ጀምሯል...")
    app.run_polling(allowed_updates=[Update.MESSAGE])

if __name__ == '__main__':
    main()
    TOKEN = "7917849176:AAH6YfXor3Vq27eQOfv6Rsc0H8m69RbyE1g"
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    TOKEN = "8941497236:AAGMV8X7GYytc2Iv2DHIQUMIogrHh1vzBGE"
    
    app = Application.builder().token(TOKEN).read_timeout(30).connect_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("ቦቱ በስኬት ስራ ጀምሯል...")
    app.run_polling(allowed_updates=[Update.MESSAGE])

if __name__ == '__main__':
    main()
