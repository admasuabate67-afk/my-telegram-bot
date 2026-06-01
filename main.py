import os
from flask import Flask
import telebot
from threading import Thread

# 1. ያመጣኸው ትክክለኛ የቦት ቶክን እዚህ ገብቷል
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8941497236:AAGMV8X7GYytc2Iv2DHIQUMIogrHh1vzBGE')
bot = telebot.TeleBot(BOT_TOKEN)

# 2. ለ Render የሚሆን ቀላል የ Flask ዌብ ሰርቨር መፍጠር
app = Flask('')

@app.route('/')
def home():
    return "ቦቱ በሰላም እየሰራ ነው!"

def run_flask():
    # Render በራሱ PORT ስለሚሰጠው ከ Environment ይቀበላል
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. የቦቱ ትዕዛዞች (Commands)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "እንኳን ደህና መጡ! ቦቱ በትክክል እየሰራ ነው።")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"የላኩት መልዕክት፡ {message.text}")

# 4. ቦቱ እና ዌብ ሰርቨሩ በአንድ ላይ እንዲሰሩ ማድረግ
if __name__ == "__main__":
    # የ Flask ሰርቨሩን ከበስተጀርባ (Background Thread) ማስነሳት
    t = Thread(target=run_flask)
    t.start()
    
    print("ቦቱ እየጀመረ ነው...")
    # ቦቱ መልዕክቶችን ሳያቋርጥ እንዲቀበል ማድረግ
    bot.infinity_polling()
    t.start()
    
    print("ቦቱ እየጀመረ ነው...")
    # ቦቱ መልዕክቶችን ሳያቋርጥ እንዲቀበል ማድረግ
    bot.infinity_polling()
