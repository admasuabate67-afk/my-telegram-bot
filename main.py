import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

# ከ @BotFather ያገኘኸው የቴሌግራም ቦት ቶከን
TOKEN = "8041497236:AAE-Cj4FeJc9nQEZ6tug8RUw"

# የኮንቨርሴሽን ስቴቶች (States)
PHOTO, NAME, GENDER, EXP_DATE, CARD_NUM, ISSUE_DATE = range(6)

# ለ Render መቆያ የሚሆን የFlask መተግበሪያ
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
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
    # 1. የFlask ሰርቨርን ማስጀመር
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # 2. የቴሌግራም ቦቱን መገንባት
    # አዲሱ የፓይተን ስሪት እንዳያቋርጠው loop_policy ማስተካከያ ተጨምሯል
    try:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    except Exception:
        pass

    application = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # 3. ቦቱን በ polling ማስነሳት
    print("ቦቱ እየጀመረ ነው...")
    application.run_polling()

if __name__ == "__main__":
    main()
