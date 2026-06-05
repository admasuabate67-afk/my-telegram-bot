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
from PIL import Image, ImageDraw, ImageFont

# በአዲሱ BotFather በሰጠህ ቶክን ተተክቷል
TOKEN = "8819848346:AAFA9M0La0b1WowDx-2m4eK7YoO50U_Xfig"

# 7ቱን መረጃዎች በቅደም ተከተል መቀበያ ደረጃዎች
PHOTO_1, NAME_2, DOB_3, GENDER_4, EXP_5, CARD_6, ISSUE_7 = range(7)

app = Flask(__name__)

@app.route('/')
def home():
    return "Template Converter Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context):
    await update.message.reply_text(
        "ሰላም! እንኳን ወደ መታወቂያ ቴምፕሌት መቀየሪያ ቦት በሰላም መጡ።\n\n"
        "እባክዎ መጀመሪያ፦\n"
        "1. 📷 የባለ መታወቂያውን **ፎቶግራፍ (ቁጥር 1)** ይላኩ።"
    )
    return PHOTO_1

async def handle_photo(update: Update, context):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"user_photo_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(photo_path)
    context.user_data['photo_1_path'] = photo_path
    
    await update.message.reply_text("✅ ፎቶው ደርሷል!\n2. 👤 **ሙሉ ስም (ቁጥር 2)** ያስገቡ (በአማርኛ እና እንግሊዘኛ)፦")
    return NAME_2

async def handle_name(update: Update, context):
    context.user_data['name_2'] = update.message.text
    await update.message.reply_text("3. 📅 **የትውልድ ቀን (ቁጥር 3)** ያስገቡ (ለምሳሌ: 14/07/1989 | 1997/Mar/23)፦")
    return DOB_3

async def handle_dob(update: Update, context):
    context.user_data['dob_3'] = update.message.text
    await update.message.reply_text("4. ⚥ **ጾታ (ቁጥር 4)** ያስገቡ (ወንድ / ሴት | Male / Female)፦")
    return GENDER_4

async def handle_gender(update: Update, context):
    context.user_data['gender_4'] = update.message.text
    await update.message.reply_text("5. ⏳ **የሚያበቃበት ቀን (ቁጥር 5)** ያስገቡ፦")
    return EXP_5

async def handle_exp_date(update: Update, context):
    context.user_data['exp_5'] = update.message.text
    await update.message.reply_text("6. 💳 **የካርድ ቁጥር FAN (ቁጥር 6)** ያስገቡ፦")
    return CARD_6

async def handle_card_num(update: Update, context):
    context.user_data['card_6'] = update.message.text
    await update.message.reply_text("7. 📅 **የተሰጠበት ቀን (ቁጥር 7)** ያስገቡ፦")
    return ISSUE_7

async def handle_issue_date(update: Update, context):
    context.user_data['issue_7'] = update.message.text
    await update.message.reply_text("⏳ ሁሉም መረጃዎች ደርሰዋል! መታወቂያውን በ Template B ላይ እያዘጋጀሁ ነው... እባክዎ በትዕግስት ይጠብቁ... ⏳")
    
    try:
        # 1. Template B ምስልን መክፈት
        template_b_path = "template_b.jpg"
        if not os.path.exists(template_b_path):
            # ፋይሉ ከሌለ ለሙከራ ያህል በስዕሉ መጠን ልክ ባዶ ምስል ይፈጥራል
            template_b = Image.new("RGB", (1034, 574), "white")
        else:
            template_b = Image.open(template_b_path)
            
        draw = ImageDraw.Draw(template_b)
        
        # 2. የአማርኛ ፎንት መጫን
        font_path = "nyala.ttf"
        font = ImageFont.truetype(font_path, 22) if os.path.exists(font_path) else ImageFont.load_default()
        # ለቁጥር 7 ለየት ያለ (የቆመ ወይም አነስ ያለ) ፎንት ለመጠቀም
        font_side = ImageFont.truetype(font_path, 18) if os.path.exists(font_path) else ImageFont.load_default()

        # 3. ✍️ መረጃዎቹን Template B ላይ በትክክለኛው ቁጥር ቦታ ላይ መጻፍ
        # [X, Y] መጋጠሚያዎችን እንደ መታወቂያህ ጥራት ማስተካከል ትችላለህ
        draw.text((420, 145), f"{context.user_data['name_2']}", fill="black", font=font) # ቁጥር 2
        draw.text((420, 245), f"{context.user_data['dob_3']}", fill="black", font=font)  # ቁጥር 3
        draw.text((420, 320), f"{context.user_data['gender_4']}", fill="black", font=font) # ቁጥር 4
        draw.text((420, 395), f"{context.user_data['exp_5']}", fill="black", font=font)   # ቁጥር 5
        draw.text((470, 480), f"{context.user_data['card_6']}", fill="black", font=font)  # ቁጥር 6
        
        # ለቁጥር 7 (በግራ በኩል በቁም ለሚጻፈው የተሰጠበት ቀን)
        # ማሳሰቢያ፡ ፅሁፉን ሙሉ በሙሉ በቁም ለማዞር የ PIL Rotate መጠቀም ይቻላል፣ ለጊዜው ቦታው ላይ ያርፋል
        draw.text((95, 250), f"{context.user_data['issue_7']}", fill="black", font=font_side)

        # 4. 🖼 ዋናውን ፎቶ (ቁጥር 1) በትልቁ ቁጥር 1 ቦታ ላይ መለጠፍ
        photo_1_path = context.user_data['photo_1_path']
        if os.path.exists(photo_1_path):
            img_1 = Image.open(photo_1_path)
            img_1_resized = img_1.resize((270, 360)) # በቁጥር 1 ሳጥን ልክ ማስተካከል
            template_b.paste(img_1_resized, (135, 130)) # የቁጥር 1 መለጠፊያ ቦታ

        # 5. 🖼 ለቁጥር 8 (የመታወቂያው ሙሉ ምስል በትንሹ "ፋይዳ" ከሚለው በታች)
        # ለዚህ ደረጃ ተጠቃሚው የላከውን ፎቶ ወይም አጠቃላይ የተሰራውን መታወቂያ በትንሹ አሳንሶ መለጠፍ ይቻላል
        if os.path.exists(photo_1_path):
            img_mini = Image.open(photo_1_path)
            img_mini_resized = img_mini.resize((80, 100)) # በቁጥር 8 ሳጥን ልክ ማሳነስ
            template_b.paste(img_mini_resized, (765, 415)) # የቁጥር 8 መለጠፊያ ቦታ

        # 6. የተሰራውን ፋይል ሴቭ አድርጎ ለተጠቃሚው መላክ
        output_file = f"final_id_{update.message.from_user.id}.jpg"
        template_b.save(output_file)
        
        await update.message.reply_photo(
            photo=open(output_file, 'rb'),
            caption="🎉 መታወቂያው በ Template B ላይ ያለምንም ስህተት ተዘጋጅቷል!"
        )
        
        # ጊዜያዊ ፋይሎችን ማጽዳት
        if os.path.exists(photo_1_path): os.remove(photo_1_path)
        if os.path.exists(output_file): os.remove(output_file)

    except Exception as e:
        await update.message.reply_text(f"ይቅርታ፣ መታወቂያውን በመስራት ላይ ስህተት አጋጥሟል፦ {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("ክዋኔው ተሰርዟል። በድጋሚ ለመጀመር /start ይጫኑ።")
    return ConversationHandler.END

def main():
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHOTO_1: [MessageHandler(filters.PHOTO, handle_photo)],
            NAME_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            DOB_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dob)],
            GENDER_4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender)],
            EXP_5: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exp_date)],
            CARD_6: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_card_num)],
            ISSUE_7: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
