import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# የቦትህ መለያ ቁልፍ (Bot Token)
TOKEN = "8941497236:AAE-C|4FeJc9nQEZ6tugHRUmIABhLCsptdA"

# የባዶ መታወቂያ ምስል ስም (በGitHub ዋናው ገጽ ላይ መኖር አለበት)
TEMPLATE_B_PATH = "template_b.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ሰላም! የ Template A ዲጂታል መታወቂያ ፎቶ ይላኩልኝ፣ ወደ Template B ቀይሬ እሰጥዎታለሁ።"
    )

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ፎቶው መላኩን ማረጋገጫ መልዕክት
    status_message = await update.message.reply_text(
        "⏳ የTemplate A መታወቂያ መረጃዎችን ወደ Template B በመቀየር ላይ ነኝ... እባክዎ ይጠብቁ።"
    )
    
    try:
        # 1. መታወቂያውን ከቴሌግራም ማውረድ
        photo_file = await update.message.photo[-1].get_file()
        input_image_path = "input_user_id.jpg"
        await photo_file.download_to_drive(input_image_path)
        
        # 2. ምስሎችን በ OpenCV ማንበብ
        img_a = cv2.imread(input_image_path)
        template_b = cv2.imread(TEMPLATE_B_PATH)
        
        if template_b is None:
            await status_message.edit_text(
                "❌ እባክዎ 'template_b.jpg' ፋይል በGitHub ሪፖዚቶሪዎ ላይ በትክክል መጫኑን ያረጋግጡ።"
            )
            return

        # 3. ባርኮዱን መቁረጥ (ቅድም ስህተት የነበረበት እና አሁን መስመሩ የተስተካከለው ኮድ)
        barcode_crop = img_a[1215:1330, 300:750]
        
        # 4. የተቆረጠውን ባርኮድ በባዶው Template B ላይ መለጠፍ
        bh, bw, _ = barcode_crop.shape
        
        # ማሳሰቢያ፦ በ template_b ላይ ባርኮዱ እንዲቀመጥበት የፈለግከው ቦታ (ቁጥሮቹን እንደ ፍላጎትህ ማስተካከል ትችላለህ)
        template_b[800:800+bh, 400:400+bw] = barcode_crop
        
        # 5. የተጠናቀቀውን አዲስ ምስል ሴቭ ማድረግ
        output_path = "output_template_b.jpg"
        cv2.imwrite(output_path, template_b)
        
        # 6. የተሰራውን መታወቂያ ለተጠቃሚው መላክ
        with open(output_path, "rb") as final_photo:
            await update.message.reply_photo(photo=final_photo, caption="✅ መታወቂያዎ በተሳካ ሁኔታ ተዘጋጅቷል!")
            
        await status_message.delete()
        
        # ጊዜያዊ ፋይሎችን ማጽዳት
        if os.path.exists(input_image_path): os.remove(input_image_path)
        if os.path.exists(output_path): os.remove(output_path)
        
    except Exception as e:
        print(f"Error: {e}")
        await status_message.edit_text(f"❌ ይቅርታ፣ መታወቂያውን መቀየር አልተቻለም። ስህተት፦ {str(e)}")

def main() -> None:
    # ቦቱን ማስነሳት
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, process_image))

    # Render ላይ ያለምንም ችግር እንዲሰራ ፖርት መክፈቻ
    port = int(os.environ.get("PORT", 8443))
    application.run_polling()

if __name__ == "__main__":
    main()
