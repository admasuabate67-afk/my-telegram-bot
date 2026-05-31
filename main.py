import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

# 1. ቦቱ ሲነሳ የሚናገረው
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! እንኳን ወደ መታወቂያ መለወጫ (Convertor) ቦት በሰላም መጡ።\n"
        "እባክዎ መጀመሪያ መታወቂያ 1 እና መታወቂያ 2ን ይላኩ።"
    )

# 2. ፎቶ ሲላክለት የሚቀበልበት እና ፕሮሰስ የሚያደርግበት ቦታ
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ፎቶው ደርሶኛል! በመቀየር ላይ ነው፣ እባክዎ ትንሽ ይጠብቁ...")
    
    # ፎቶውን ማውረድ
    photo_file = await update.message.photo[-1].get_file()
    input_path = f"user_{update.message.chat_id}.jpg"
    await photo_file.download_to_drive(input_path)
    
    # እዚህ ጋ የ Conversion (የመቀየር) ሎጂክ ይገባል
    # ለምሳሌ: easyocr እና Pillow በመጠቀም Template Aን ወደ Template B መቀየር
    
    output_path_3 = f"converted_3_{update.message.chat_id}.jpg"
    output_path_4 = f"converted_4_{update.message.chat_id}.jpg"
    
    # ለጊዜው የመነሻ ማሳያ (ይህ በራስህ የ Pillow logic ይተካል)
    img = Image.open(input_path)
    img.save(output_path_3) # ናሙና
    img.save(output_path_4) # ናሙና

    # የተዘጋጁትን አዳዲስ መታወቂያዎች መለስክ መላክ
    await update.message.reply_photo(photo=open(output_path_3, 'rb'), caption="ይህ 3ኛው መታወቂያ ነው")
    await update.message.reply_photo(photo=open(output_path_4, 'rb'), caption="ይህ 4ኛው መታወቂያ ነው")

    # ጊዜያዊ ፋይሎችን ማጽዳት
    os.remove(input_path)
    os.remove(output_path_3)
    os.remove(output_path_4)

def main():
8941497236:AAGMV8X7GYytc2Iv2DHIQUMIogrHh1vzBGE"
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("ቦቱ ስራ ጀምሯል...")
    app.run_polling()

if __name__ == '__main__':
    main()
