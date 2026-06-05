import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. የቦት ቶከንዎን እዚህ ያስገቡ
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

def resize_to_match(source, target_width, target_height):
    """የተቆረጠውን ምስል ወደ Template B ሳጥን መጠን በትክክል ማስተካከያ ዘዴ"""
    return cv2.resize(source, (target_width, target_height), interpolation=cv2.INTER_AREA)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 እንኳን ደህና መጡ! እባክዎን የ Template A መታወቂያ ፎቶ ይላኩልኝ። ወደ Template B ቀይሬ እሰጥዎታለሁ።")

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ መረጃዎችን በመልቀም ላይ ነኝ... እባክዎን ጥቂት ሰከንዶች ይጠብቁ።")
    
    photo_file = await update.message.photo[-1].get_file()
    input_path = "user_input_a.jpg"
    await photo_file.download_to_drive(input_path)
    
    try:
        template_b_path = "template_b.jpg" # እርስዎ የላኩት ባዶ Template B ምስል በፎልደሩ ውስጥ መኖር አለበት
        if not os.path.exists(template_b_path):
            await update.message.reply_text("❌ ስህተት፡ 'template_b.jpg' የተባለው ባዶ ምስል ሰርቨሩ ላይ አልተገኘም።")
            return

        # ምስሎቹን ማንበብ
        img_a = cv2.imread(input_path)
        img_b = cv2.imread(template_b_path)
        
        # ምስሎቹ መደበኛ መጠን ላይ መሆናቸውን ማረጋገጥ (ለምሳሌ፡ 1000 x 1500)
        # ይህም የመቁረጫ ቦታዎቹ ሁልጊዜ ትክክል እንዲሆኑ ይረዳል
        img_a = cv2.resize(img_a, (1000, 1500))
        img_b = cv2.resize(img_b, (1500, 1000)) # Template B አግድም (Landscape) ስለሆነ

        # --- ደረጃ 1፡ መረጃዎችን ከ Template A ላይ መቁረጥ (Crop) ---
        # [ymin, xmin, ymax, xmax] መጋጠሚያዎች
        main_photo_crop = img_a[330:780, 310:590]      # 1. ዋናው ፎቶ
        name_crop       = img_a[610:660, 200:680]      # 2. ሙሉ ስም
        dob_crop        = img_a[675:715, 200:680]      # 3. የትውልድ ቀን
        sex_crop        = img_a[725:765, 200:680]      # 4. ጾታ
        expiry_crop     = img_a[775:815, 200:680]      # 5. የሚያበቃበት ቀን
        card_num_crop   = img_a[825:875, 330:680]      # 6. ካርድ ቁጥር (FAN)
        issue_date_crop = img_a[330:780, 900:950]      # 7. የተሰጠበት ቀን (በቁም ያለው)

        # --- ደረጃ 2፡ የተቆረጡትን ምስሎች ወደ Template B ላይ መለጠፍ ---
        # በእያንዳንዱ ሳጥን መጠን ልክ ምስሉን Resize እያደረገ ይለጥፋል
        
        # 1. ዋናው ፎቶ (ቦታ 1) -> ሳጥን መጠን (ስፋት: 380, ቁመት: 620)
        img_b[260:880, 130:510] = resize_to_match(main_photo_crop, 380, 620)
        
        # 2. ሙሉ ስም (ቦታ 2) -> ሳጥን መጠን (ስፋት: 400, ቁመት: 110)
        img_b[300:410, 410:810] = resize_to_match(name_crop, 400, 110)
        
        # 3. የትውልድ ቀን (ቦታ 3) -> ሳጥን መጠን (ስፋት: 390, ቁመት: 70)
        img_b[460:530, 410:800] = resize_to_match(dob_crop, 390, 70)
        
        # 4. ጾታ (ቦታ 4) -> ሳጥን መጠን (ስፋት: 390, ቁመት: 60)
        img_b[560:620, 410:800] = resize_to_match(sex_crop, 390, 60)
        
        # 5. የሚያበቃበት ቀን (ቦታ 5) -> ሳጥን መጠን (ስፋት: 400, ቁመት: 60)
        img_b[670:730, 410:810] = resize_to_match(expiry_crop, 400, 60)
        
        # 6. ካርድ ቁጥር (ቦታ 6) -> ሳጥን መጠን (ስፋት: 350, ቁመት: 130)
        img_b[570:700, 460:810] = resize_to_match(card_num_crop, 350, 130)
        
        # 7. የተሰጠበት ቀን (ቦታ 7) -> ሳጥን መጠን (ስፋት: 50, ቁመት: 800)
        img_b[85:885, 90:140] = resize_to_match(issue_date_crop, 50, 800)
        
        # 8. ትንሿ ፎቶ ከፋይዳ በታች (ቦታ 8) -> ዋናውን ፎቶ አሳንሶ መለጠፍ (ስፋት: 110, ቁመት: 170)
        img_b[720:890, 740:850] = resize_to_match(main_photo_crop, 110, 170)

        # ውጤቱን ሴቭ ማድረግ
        output_path = "final_fayda_b.jpg"
        cv2.imwrite(output_path, img_b)
        
        # ለተጠቃሚው መላክ
        await update.message.reply_photo(
            photo=open(output_path, 'rb'), 
            caption="✅ መረጃዎቹ ከ Template A ላይ ተለቅመው ወደ Template B ላይ በትክክል ገብተዋል!"
        )
        
        # ጊዜያዊ ፋይሎችን ማጽዳት
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        await update.message.reply_text(f"❌ ስህተት አጋጥሟል፦ {str(e)}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(filters.PHOTO, process_image)
    print("ቦቱ ስራ ጀምሯል...")
    application.run_polling()

if __name__ == "__main__":
    main()
