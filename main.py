import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from PIL import Image

# ከ @BotFather ያገኘኸው የቴሌግራም ቦት ቶከን
TOKEN = "8041497236:AAE-Cj4FeJc9nQEZ6tug8RUw"

# የኮንቨርሴሽን ስቴቶች (States)
PHOTO, NAME, GENDER, EXP_DATE, CARD_NUM, ISSUE_DATE = range(6)

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

async def main_async():
    # ቦቱን ማዘጋጀት
    application = ApplicationBuilder().token(TOKEN).build()
    
    # የኮንቨርሴሽን ማስተናገጃ (Conversation Handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # ቦቱን ማስተናገጃ መጀመር
    print("ቦቱ በተሳካ ሁኔታ እየሰራ ነው...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # ቦቱ ሳይጠፋ እንዲቆይ ማድረግ
    while True:
        await asyncio.sleep(1)

def main():
    # የ Event Loop ስህተትን የሚፈታው ዋናው መስመር
    try:
        asyncio.run(main_async())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main_async())

if __name__ == "__main__":
    main()
