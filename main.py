import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image

# ከ @BotFather ያገኘኸው ትክክለኛው የቦት ቶክን (ያለ ምንም ክፍተት)
TOKEN = "8941497236:AAE-C|4FeJc9nQEZ6tugHRUmIABhLCsptdA"

# ተጠቃሚው /start ሲል የሚመጣው መልእክት
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! የ 'Efid Convert Bot' በተሳካ ሁኔታ ተነሥቷል።\n"
        "ለመቀጠል እባክህ የምትፈልገውን ፋይል ወይም ትዕዛዝ አስገባ።"
    )

def main():
    # አዲሱ የ v20+ አፕሊኬሽን አገነባብ መዋቅር
    application = ApplicationBuilder().token(TOKEN).build()

    # የ /start ኮማንድ አስተናጋጅ መመዝገብ
    application.add_handler(CommandHandler("start", start))

    # ቦቱን በ polling ስልት ማስነሳት (የ event loop ችግርን ይፈታል)
    print("ቦቱ በተሳካ ሁኔታ እየሰራ ነው...")
    application.run_polling()

if __name__ == "__main__":
    main()
    y_position = 450  
        
        # ፎቶውን Template B ላይ መለጠፍ
        template_b.paste(user_photo, (x_position, y_position), user_photo)
        
        # ማስታወሻ፡ ጽሑፎችን (ስም፣ ጾታ ወዘተ) በምስሉ ላይ መጨመር ከፈለጉ ImageDraw መጠቀም ይቻላል።
        # ለጊዜው ፎቶውን ብቻ ቁጥር 8 ቦታ ላይ የማስገባት ስራ እዚህ ላይ ተሰርቷል።
        
        # የተጠናቀቀውን ምስል ማስቀመጥ
        output_path = "final_efid.png"
        template_b.save(output_path)
        
        # ለተጠቃሚው መልሶ መላክ
        with open(output_path, 'rb') as document:
            await update.message.reply_document(document=document, filename="EFID_Card.png", caption="የእርስዎ ፋይዳ ካርድ ተዘጋጅቷል! ✅")
            
    except Exception as e:
        await update.message.reply_text(f"ምስሉን በማዘጋጀት ላይ ስህተት አጋጥሟል፡ {str(e)}")
        
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("ክዋኔው ተሰርዟል።")
    return ConversationHandler.END

def main():
    # ቦቱን ማስነሳት
    application = Application.builder().token(TOKEN).build()

    # የውይይት ቅደም ተከተል (Conversation Handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, photo_handler)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_handler)],
            EXP_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, exp_date_handler)],
            CARD_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, card_num_handler)],
            ISSUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, issue_date_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    
    # ቦቱን ማሰራት
    print("ቦቱ ስራ ጀምሯል...")
    application.run_polling()

if __name__ == '__main__':
    main()
