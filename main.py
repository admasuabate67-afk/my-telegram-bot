import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from PIL import Image

# Token አስገባ
TOKEN = "8941497236:AAE-C|4FeJc9nQEZ6tugHRUmIABh LCsptdA"

# የቦት ስቴቶች (የደረጃ መቆጣጠሪያ)
PHOTO, NAME, GENDER, EXP_DATE, CARD_NUM, ISSUE_DATE = range(6)

# Logging ማስተካከያ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "እንኳን ወደ EFID Convert ቦት በሰላም መጡ! 👋\n\n"
        "ለመጀመር እባክዎ መጀመሪያ **የባለቤቱን ፎቶ** ይላኩ።"
    )
    return PHOTO

async def photo_handler(update: Update, context: CallbackContext) -> int:
    # ፎቶውን ማውረድ
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive('user_photo.jpg')
    
    await update.message.reply_text("በጣም ጥሩ! አሁን ደግሞ **ሙሉ ስም** ያስገቡ፡")
    return NAME

async def name_handler(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("እባክዎ **ጾታ** ያስገቡ (ወንድ/ሴት)፡")
    return GENDER

async def gender_handler(update: Update, context: CallbackContext) -> int:
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("እባክዎ **የሚያበቃበት ቀን** ያስገቡ (በኢትዮጵያ ወይም በአውሮፓውያን አቆጣጠር)፡")
    return EXP_DATE

async def exp_date_handler(update: Update, context: CallbackContext) -> int:
    context.user_data['exp_date'] = update.message.text
    await update.message.reply_text("እባክዎ **የካርድ ቁጥር** ያስገቡ፡")
    return CARD_NUM

async def card_num_handler(update: Update, context: CallbackContext) -> int:
    context.user_data['card_num'] = update.message.text
    await update.message.reply_text("በመጨረሻም **የተሰጠበት ቀን** ያስገቡ፡")
    return ISSUE_DATE

async def issue_date_handler(update: Update, context: CallbackContext) -> int:
    context.user_data['issue_date'] = update.message.text
    await update.message.reply_text("መረጃው እየተዘጋጀ ነው... እባክዎ ጥቂት ሰከንዶችን ይጠብቁ። ⏳")
    
    # ፎቶዎችን የማቀናበር ሂደት (Image Processing)
    try:
        # Template B ምስልን መክፈት (እዚህ ጋር template_b.png የሚለው ፋይል በኮዱ አጠገብ መኖር አለበት)
        template_b = Image.open("template_b.png").convert("RGBA")
        user_photo = Image.open("user_photo.jpg").convert("RGBA")
        
        # 📌 የፎቶ መጠን ማስተካከያ (እንደ Template B ቁጥር 8 ቦታ መጠን ይለወጣል)
        # ለምሳሌ፡ ስፋት 200px፣ ቁመት 250px ካስፈለገ
        photo_width = 200 
        photo_height = 250
        user_photo = user_photo.resize((photo_width, photo_height))
        
        # 📌 የፎቶ ማስቀመጫ ቦታ (X እና Y Coordinates)
        # በTemplate B ላይ "ፋይዳ" ከሚለው ጽሑፍ በታች ቁጥር 8 ያለበትን ቦታ ይለኩና እዚህ ይተኩት
        x_position = 150  
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
