import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

# ከ @BotFather ያገኘኸው የቴሌግራም ቦት ቶከን
TOKEN = "8041497236:AAE-Cj4FeJc9nQEZ6tug8RUw"

# የኮንቨርሴሽን ስቴቶች (States)
PHOTO, NAME, GENDER, EXP_DATE, CARD_NUM, ISSUE_DATE = range(6)

# ለ Render መቆያ የሚሆን አነስተኛ የFlask መተግበሪያ
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render የሚሰጠውን ፖርት ፈልጎ በዚያ ላይ ሰርቨሩን ያስነሳል
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ተጠቃሚው /start ሲል የሚመጣው መልዕክት
async def start(update: Update, context):
    await update.message.reply_text(
        "ሰላም! የ 'Efid Convert Bot' በሰላም ደርሰዋል።\n"
        "ለመቀጠል እባክህ የምትፈልገውን ፋይል ወይም ትዕዛዝ አስገባ።"
    )
    return PHOTO

# ፎቶዎችን የሚያስተናግደውና ኤዲት የሚያደርገው ዋናው ክፍል
async def handle_photo(update: Update, context):
    try:
        await update.message.reply_text("ምስሉ በተሳካ ሁኔታ ተዘጋጅቷል!")
    except Exception as e:
        await update.message.reply_text(f"ምስሉን ሲያዘጋጅ ስህተት አጋጥሟል: {e}")
    return ConversationHandler.END

# ስራን ለማቋረጥ (Cancel)
async def cancel(update: Update, context):
    await update.message.reply_text("ክዋኔው ተሰርዟል።")
    return ConversationHandler.END

def main():
    # 1. መጀመሪያ የFlask ዌብ ሰርቨሩን በሌላ Thread (ጀርባ) ላይ ማስጀመር
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. የቴሌግራም ቦቱን ማዋቀር
    application = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # 3. ቦቱን በንፅህና ማስጀመር (ይህ በአዲሱ ስሪት አስተማማኙ መንገድ ነው)
    print("ቦቱ እና ዌብ ሰርቨሩ በተሳካ ሁኔታ እየሰሩ ነው...")
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
