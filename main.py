import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# የቦት ማረጋገጫ ቁጥር (Bot Token)
TOKEN = "8941497236:AAE-C|4FeJc9nQEZ6tugHRU" # ማስታወሻ፦ እውነተኛውን ቶክንዎን እዚህ ያስገቡ

# የባዶ መታወቂያ ምስል መንገድ
TEMPLATE_B_PATH = "template_b.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! የ Template A ዲጂታል መታወቂያ ፎቶ ይላኩና ወደ Template B ቀይሬ እሰጥዎታለሁ።"
    )

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # የሂደት ማረጋገጫ መልዕክት
    status_message = await update.message.reply_text(
        "⏳ የTemplate A መታወቂያ መረጃዎችን ወደ Template B በመቀየር ላይ ነኝ... እባክዎ ይጠብቁ..."
    )
    
    input_image_path = "input_user_id.jpg"
    output_path = "output_template_b.jpg"

    try:
        # 1. ፎቶውን ከቴሌግራም ማውረድ
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(input_image_path)

        # 2. ምስሎችን በ OpenCV ማንበብ
        img_a = cv2.imread(input_image_path)
        template_b = cv2.imread(TEMPLATE_B_PATH)

        if template_b is None:
            await status_message.edit_text(
                "❌ ይቅርታ፤ መታወቂያውን መቀየር አልተቻለም። template_b.jpg ፋይል በGitHub ላይ በትክክል መጫኑን ያረጋግጡ።"
            )
            return

        # 3. ባርኮድ መቁረጥ (እንደ መጀመሪያው ኮድዎ መጋጠሚያ)
        # ማስታወሻ፦ የቁረጥ ቦታዎችን (Coordinates) እንደ አስፈላጊነቱ ማስተካከል ይችላሉ
        barcode_crop = img_a[1215:1330, 300:700]
        bh, bw, _ = barcode_crop.shape

        # 4. የተቆረጠውን ባርኮድ በ Template B ላይ ማሳረፍ
        template_b[800:800+bh, 400:400+bw] = barcode_crop

        # 5. የተስተካከለውን አዲስ ምስል ሴቭ ማድረግ
        cv2.imwrite(output_path, template_b)

        # 6. የተሰራውን መታወቂያ ለተጠቃሚው መላክ
        with open(output_path, "rb") as final_photo:
            await update.message.reply_photo(photo=final_photo, caption="✅ እነሆ የተስተካከለው መታወቂያዎ!")

        # የሂደት መልዕክቱን ማጥፋት
        await status_message.delete()

    except Exception as e:
        print(f"Error: {e}")
        await status_message.edit_text(f"❌ ስህተት አጋጥሟል፦ {str(e)}")
    
    finally:
        # ጊዜያዊ ፋይሎችን ማጽዳት
        if os.path.exists(input_image_path):
            os.remove(input_image_path)
        if os.path.exists(output_path):
            os.remove(output_path)

def main() -> None:
    # ቦቱን ማስነሳት
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, process_image))

    # Render ላይ እንዲሠራ የፖርት ማስተካከያ
    port = int(os.environ.get("PORT", 8443))
    application.run_polling()

if __name__ == "__main__":
    main()
