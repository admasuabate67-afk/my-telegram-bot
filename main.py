import os
from flask import Flask
import telebot
from threading import Thread

# 1. የቦት ቶከን ማዋቀር (በ Render Environment Variables ላይ 'BOT_TOKEN' በሚል ያስገቡት)
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'እዚህ ጋር የቦት ቶከንዎን መፃፍም ይችላሉ')
bot = telebot.TeleBot(BOT_TOKEN)

# 2. ለ Render የሚሆን አነስተኛ የ Flask ዌብ ሰርቨር መፍጠር
app = Flask('')

@app.route('/')
def home():
    return "ቦቱ በሰላም እየሰራ ነው!"

def run_flask():
    # Render በራሱ PORT ስለሚሰጥ ከ Environment Variable ያነባል
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. የቦቱ ትዕዛዞች (Commands)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "እንኳን ደህና መጡ! ቦቱ ዝግጁ ነው::")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"የላኩት መልዕክት፦ {message.text}")

# 4. ቦቱ እና ዌብ ሰርቨሩ በአንድ ላይ እንዲሰሩ ማድረግ
if __name__ == "__main__":
    # የ Flask ሰርቨሩን ከበስተጀርባ (Background) ማስጀመር
    t = Thread(target=run_flask)
    t.start()
    
    print("ቦቱ እየጀመረ ነው...")
    # ቦቱ መልዕክቶችን ያለማቋረጥ እንዲቀበል ማድረግ
    bot.infinity_polling()
        
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
