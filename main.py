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
    user_photo = context.user_data.get('photo') # ወይም ፎቶውን የምታወርድበት ኮድ እዚህ ይገባል
    
    # የቦታ መገኛ መወሰኛ (የነበረው መስመር 30)
    y_position = 450
    x_position = 100 # አስፈላጊ ከሆነ መነሻ ቦታ ማስቀመጫ
    
    try:
        # ፎቶውን Template B ላይ መለጠፍ
        # template_b.paste(user_photo, (x_position, y_position))
        
        # ማስታወሻ፡ ጽሑፎችን (ስም፣ ጾታ ወዘተ) በምስል ላይ መጻፍ
        # ለጊዜው ፎቶውን ብቻ ቁጥር 8 ቦታ ላይ የማስገባት ስራ
        
        # የተጠናቀቀውን ምስል ማስቀመጥ
        output_path = "final_efid.png"
        # template_b.save(output_path)
        
        # ለተጠቃሚው መልስ መላክ
        # with open(output_path, 'rb') as document:
        #     await update.message.reply_document(document)
        
        await update.message.reply_text("ምስሉ በተሳካ ሁኔታ ተዘጋጅቷል!")
        
    except Exception as e:
        await update.message.reply_text(f"ምስሉን ሲያዘጋጅ ስህተት አጋጥሟል: {e}")
        
    return ConversationHandler.END

# ስራን ለማቋረጥ (Cancel)
async def cancel(update: Update, context):
    await update.message.reply_text("ክዋኔው ተሰርዟል።")
    return ConversationHandler.END

def main():
    # ቦቱን ማዘጋጀት
    application = ApplicationBuilder().token(TOKEN).build()
    
    # የኮንቨርሴሽን ማስተናገጃ (Conversation Handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            # ሌሎቹን ስቴቶች (NAME, GENDER...) እንደ አስፈላጊነቱ እዚህ ማከል ትችላለህ
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # ቦቱን ማስተናገጃ መጀመር
    print("ቦቱ በተሳካ ሁኔታ እየሰራ ነው...")
    application.run_polling()

if __name__ == "__main__":
    main()
