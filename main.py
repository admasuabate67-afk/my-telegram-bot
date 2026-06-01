import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

# 1. ቦቱ ሲነሳ የሚናገረው ሰላምታ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! እንኳን ወደ መታወቂያ መለወጫ (Convertor) ቦት በሰላም መጡ።\n"
        "እባክህ ለመቀየር የምትፈልገውን የቆየ መታወቂያ ፎቶ (Template A) ላክልኝ።"
    )

# 2. ፎቶ ሲላክለት ቆርጦ የሚለጥፍበት ዋናው ክፍል
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("መታወቂያው ደርሶኛል! መረጃዎችን ወደ አዲሱ Template በመቀየር ላይ ነው፣ እባክዎ ይጠብቁ...")
    
    input_path = f"user_{update.message.chat_id}.jpg"
    output_path = f"converted_{update.message.chat_id}.jpg"
    template_b_path = "template_b.jpg"

    try:
        # ፎቶውን ማውረድ
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(input_path)
        
        # ሁለቱንም መታወቂያዎች መክፈት
        img_a = Image.open(input_path)
        
        # template_b.jpg ከሌለ ወይም የተበላሸ ከሆነ አዲስ ባዶ ምስል በራሱ ይፈጥራል
        if not os.path.exists(template_b_path) or os.path.getsize(template_b_path) < 100:
            # ትክክለኛ የአዲስ መታወቂያ መጠን (ለምሳሌ 1000x600) ባዶ ነጭ ምስል ይፈጥራል
            img_b = Image.new("RGB", (1012, 638), (255, 255, 255))
        else:
            try:
                img_b = Image.open(template_b_path)
            except:
                img_b = Image.new("RGB", (1012, 638), (255, 255, 255))

        # የፎቶ መቁረጫ ቦታዎች (ክሮፕ ማድረጊያ)
        # 1. ፎቶ (Photo)
        photo_box = (670, 180, 890, 480)
        cropped_photo = img_a.crop(photo_box)
        img_b.paste(cropped_photo, (700, 150))

        # 2. ሙሉ ስም (Full Name)
        name_box = (50, 180, 500, 240)
        cropped_name = img_a.crop(name_box)
        img_b.paste(cropped_name, (400, 240))

        # 3. የልደት ቀን (DOB)
        dob_box = (50, 260, 500, 310)
        cropped_dob = img_a.crop(dob_box)
        img_b.paste(cropped_dob, (400, 330))

        # ሴቭ አድርጎ ለተጠቃሚው መላክ
        img_b.save(output_path)
        await update.message.reply_photo(photo=open(output_path, 'rb'), caption="🎉 እንኳን ደስ አለዎት! መታወቂያዎ በተሳካ ሁኔታ ተቀይሯል።")

        # ጊዜያዊ ፋይሎችን ማጽዳት
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

    except Exception as e:
        await update.message.reply_text(f"💡 ስህተት ተከስቷል፦ የላኩት ፎቶ ግልጽ መሆኑን ያረጋግጡ።")
        if os.path.exists(input_path): os.remove(input_path)

def main():
    # የአንተ ቦት ቶከን
    TOKEN = "7917849176:AAH6YfXor3Vq27eQOfv6Rsc0H8m69RbyE1g"
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    TOKEN = "8941497236:AAGMV8X7GYytc2Iv2DHIQUMIogrHh1vzBGE"
    
    app = Application.builder().token(TOKEN).read_timeout(30).connect_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("ቦቱ በስኬት ስራ ጀምሯል...")
    app.run_polling(allowed_updates=[Update.MESSAGE])

if __name__ == '__main__':
    main()
