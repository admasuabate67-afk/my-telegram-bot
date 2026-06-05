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

# ያንተ እውነተኛ እና ትኩስ ቦት ቶከን ከ BotFather
TOKEN = "8819848346:AAFA9M0La0b1WowDx-2m4eK7YoO50U_Xfig"

# የኮንቨርዥን ደረጃዎች (Conversation States)
PHOTO, NAME, GENDER, EXP_DATE, CARD_NUM, ISSUE_DATE = range(6)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    # Render የሚሰጠውን PORT በራስ-ሰር ይወስዳል
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context):
    await update.message.reply_text(
        "ሰላም! የ 'Efid Convert Bot' በሰላም ደርሰዋል።\n"
        "ለመቀጠል እባክህ መጀመሪያ ፎቶግራፍህን ላክልኝ።"
    )
    return PHOTO

async def handle_photo(update: Update, context):
    try:
        # እዚህ ጋር ለወደፊት የፎቶ ማስተካከያ (Pillow) ኮድህን ማስገባት ትችላለህ
        await update.message.reply_text("ምስሉ በተሳካ ሁኔታ ደርሶኛል! አሁን ደግሞ ሙሉ ስምህን አስገባ።")
        return NAME
    except Exception as e:
        await update.message.reply_text(f"በፎቶው ላይ ስህተት ተፈጥሯል: {e}")
        return ConversationHandler.END

async def handle_name(update: Update, context):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("ጾታህን አስገባ (ወንድ/ሴት)፦")
    return GENDER

async def handle_gender(update: Update, context):
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("የማውጫ ቀን (Issue Date) አስገባ፦")
    return ISSUE_DATE

async def handle_issue_date(update: Update, context):
    context.user_data['issue_date'] = update.message.text
    await update.message.reply_text("የሚያበቃበትን ቀን (Expiry Date) አስገባ፦")
    return EXP_DATE

async def handle_exp_date(update: Update, context):
    context.user_data['exp_date'] = update.message.text
    await update.message.reply_text("የካርድ ቁጥር (Card Number) አስገባ፦")
    return CARD_NUM

async def handle_card_num(update: Update, context):
    context.user_data['card_num'] = update.message.text
    
    # ሁሉንም መረጃዎች ተቀብሎ ሲጨርስ ለተጠቃሚው የሚያሳየው ማጠቃለያ
    summary = (
        "ሁሉም መረጃዎች በተሳካ ሁኔታ ተመዝግበዋል! 🎉\n\n"
        "የመጣው መረጃ ማጠቃለያ፦\n"
        f"👤 ስም: {context.user_data.get('name')}\n"
        f"⚥ ጾታ: {context.user_data.get('gender')}\n"
        f"📅 የፎርማት ቀን: {context.user_data.get('issue_date')}\n"
        f"⏳ የሚያበቃበት: {context.user_data.get('exp_date')}\n"
        f"💳 ካርድ ቁጥር: {context.user_data.get('card_num')}"
    )
    await update.message.reply_text(summary)
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("ክዋኔው ተሰርዟል። በድጋሚ ለመጀመር /start ይጫኑ።")
    return ConversationHandler.END

def main():
    # 1. የ Flask ሰርቨርን በጀርባ (Background) በ Thread ማስጀመር
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. የቴሌግራም ቦት መገንባት
    application = ApplicationBuilder().token(TOKEN).build()
    
    # 3. የውይይት ፍሰቱን (Conversation Handler) መዘርጋት
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender)],
            ISSUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue_date)],
            EXP_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exp_date)],
            CARD_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_card_num)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # 4. ቦቱን በ Polling መንገድ ማነሳሳት
    print("ቦቱ በተሳካ ሁኔታ እየሰራ ነው...")
    application.run_polling()

if __name__ == "__main__":
    main()
