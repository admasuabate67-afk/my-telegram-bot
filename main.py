import os
import asyncio
import sys
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
8819848346:
AAEtkHmyTau8Kbphaj51BzDECcbS2hFf2-I
# የፓይተን ስሪት 3.14+ ከሆነ የሚመጣውን የ loop ችግር ለመፍታት
if sys.version_info >= (3, 12):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

TOKEN = "8041497236:AAE-Cj4FeJc9nQEZ6tug8RUw"
PHOTO, NAME, GENDER, EXP_DATE, CARD_NUM, ISSUE_DATE = range(6)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context):
    await update.message.reply_text(
        "ሰላም! የ 'Efid Convert Bot' በሰላም ደርሰዋል።\n"
        "ለመቀጠል እባክህ የምትፈልገውን ፋይል ወይም ትዕዛዝ አስገባ።"
    )
    return PHOTO

async def handle_photo(update: Update, context):
    try:
        await update.message.reply_text("ምስሉ በተሳካ ሁኔታ ተዘጋጅቷል!")
    except Exception as e:
        await update.message.reply_text(f"ስህተት: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("ክዋኔው ተሰርዟል።")
    return ConversationHandler.END

async def main_async():
    # 1. የቴሌግራም ቦቱን መገንባት
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # 2. ቦቱን በአስተማማኝ ሁኔታ ማስጀመር
    await application.initialize()
    await application.start()
    print("ቦቱ በተሳካ ሁኔታ ተነስቷል...")
    
    # Render እንዳይዘጋው በየሴኮንዱ ንቁ ሆኖ እንዲጠብቅ ማድረግ
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1)

def main():
    # የFlask ሰርቨርን በጀርባ Thread ማስጀመር
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # ዋናውን የቦት ስራ ማስጀመር
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
