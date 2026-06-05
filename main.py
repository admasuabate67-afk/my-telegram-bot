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

TOKEN = "8941497236:AAE-Cl4FeJc9nQEZ6tugHRUmIABhLCsptdA"

# 7ቱን የመረጃ ደረጃዎች በቅደም ተከተል ማዘጋጀት
PHOTO, NAME, DOB, GENDER, EXP_DATE, CARD_NUM, ISSUE_DATE = range(7)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context):
    await update.message.reply_text(
        "ሰላም! የ 'Efid Convert Bot' በሰላም ደርሰዋል።\n\n"
        "የመታወቂያ ቴምፕሌት ለመቀየር እባክዎ መጀመሪያ ፦\n"
        "1. 📷 **ፎቶግራፍዎን** ይልኩ።"
    )
    return PHOTO

async def handle_photo(update: Update, context):
    photo_file = await update.message.photo[-1].get_file()
    user_photo_path = f"user_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(user_photo_path)
    context.user_data['photo_path'] = user_photo_path
    
    await update.message.reply_text("✅ ፎቶው ደርሷል!\n2. 👤 **ሙሉ ስምዎን** ያስገቡ፦")
    return NAME

async def handle_name(update: Update, context):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("3. 📅 **የትውልድ ቀን** (Birth Date) ያስገቡ፦")
    return DOB

async def handle_dob(update: Update, context):
    context.user_data['dob'] = update.message.text
    await update.message.reply_text("4. ⚥ **ጾታ** (ወንድ/ሴት) ያስገቡ፦")
    return GENDER

async def handle_gender(update: Update, context):
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("5. ⏳ **የሚያበቃበት ቀን** (Expiry Date) ያስገቡ፦")
    return EXP_DATE

async def handle_exp_date(update: Update, context):
    context.user_data['exp_date'] = update.message.text
    await update.message.reply_text("6. 💳 **የካርድ ቁጥር** (Card Number) ያስገቡ፦")
    return CARD_NUM

async def handle_card_num(update: Update, context):
    context.user_data['card_num'] = update.message.text
    await update.message.reply_text("7. 📅 **የተሰጠበት ቀን** (Issue Date) ያስገቡ፦")
    return ISSUE_DATE

async def handle_issue_date(update: Update, context):
    context.user_data['issue_date'] = update.message.text
    await update.message.reply_text("⏳ መረጃዎቹ ተሰብስበዋል! መታወቂያው በ Template B ላይ እየተዘጋጀ ነው፣ እባክዎ በትዕግስት ይጠብቁ...")
    
    try:
        # Template B ምስልን መክፈት (ፋይሉ በስተጀርባ መኖር አለበት)
        # ከሌለ በቦቱ ፎልደር ውስጥ 'template_b.jpg' በሚል ስም ባዶውን መታወቂያ አስቀምጥ
        template_path = "template_b.jpg"
        
        if not os.path.exists(template_path):
            # ፋይሉ ከሌለ ለሙከራ ያህል ባዶ ነጭ ምስል ይፈጥራል
            template = Image.new("RGB", (1000, 650), "white")
        else:
            template = Image.open(template_path)
            
        draw = ImageDraw.Draw(template)
        
        # የአማርኛ ፎንት (nyala.ttf በፎልደሩ ውስጥ መኖር አለበት)
        font_path = "nyala.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 26)
        else:
            font = ImageFont.load_default()

        # ✍️ መረጃዎቹን Template B ላይ መጻፍ 
        # (ቁጥሮቹን [X, Y] ያንተ መታወቂያ ዲዛይን ላይ ወደሚገኘው ክፍት ቦታ አስተካክላቸው)
        draw.text((350, 150), f"ስም: {context.user_data['name']}", fill="black", font=font)
        draw.text((350, 200), f"ትውልድ ቀን: {context.user_data['dob']}", fill="black", font=font)
        draw.text((350, 250), f"ጾታ: {context.user_data['gender']}", fill="black", font=font)
        draw.text((350, 300), f"የተሰጠበት ቀን: {context.user_data['issue_date']}", fill="black", font=font)
        draw.text((350, 350), f"የሚያበቃበት ቀን: {context.user_data['exp_date']}", fill="black", font=font)
        draw.text((350, 400), f"የካርድ ቁጥር: {context.user_data['card_num']}", fill="black", font=font)

        # 🖼 "ፋይዳ" ከሚለው ጽሑፍ በታች ቁጥር 8 በነበረበት ቦታ ላይ የተጠቃሚውን ፎቶ መለጠፍ
        user_photo_path = context.user_data['photo_path']
        if os.path.exists(user_photo_path):
            user_img = Image.open(user_photo_path)
            # የፎቶውን መጠን ወደ መታወቂያው ፍሬም ማስተካከል (ለምሳሌ 180x220)
            user_img = user_img.resize((180, 220))
            
            # (X=80, Y=250) ቁጥር 8 ያለበትን ትክክለኛ መጋጠሚያ እዚህ ቦታ ላይ ተካው
            template.paste(user_img, (80, 250))
            
        # የተሰራውን የመጨረሻ መታወቂያ ሴቭ ማድረግ
        output_path = f"result_{update.message.from_user.id}.jpg"
        template.save(output_path)
        
        # ለተጠቃሚው መላክ
        await update.message.reply_photo(
            photo=open(output_path, 'rb'), 
            caption="🎉 መታወቂያዎ በ Template B ላይ በተሳካ ሁኔታ ተዘጋጅቷል!"
        )
        
        # ጊዜያዊ ፋይሎችን ከሰርቨሩ ላይ ማጽዳት
        if os.path.exists(user_photo_path): os.remove(user_photo_path)
        if os.path.exists(output_path): os.remove(output_path)
        
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
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dob)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender)],
            EXP_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exp_date)],
            CARD_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_card_num)],
            ISSUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
