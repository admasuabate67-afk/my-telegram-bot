import os
import logging
import sqlite3
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from PIL import Image

# Logging ማዋቀር
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App ማዘጋጀት (ለRender ዌብሁክ)
app = Flask(__name__)

# ማስታወሻ፦ ቶከኑን በRender Environment Variables ላይ "BOT_TOKEN" በሚል ስም ያስገቡት።
# አድሚን አይዲ ደግሞ የእርስዎን የቴሌግራም ID ያስገቡበት (ፖይንት ለመጨመር)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8941497236:AAE-Cl4FeJc9nQEZ6tugHRUmIABhLCsptdA")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789")) # የእርስዎን ትክክለኛ ID እዚህ ይተኩ

# 1. ዳታቤዝ ማዋቀር (የተጠቃሚዎችን ፖይንት ለመያዝ)
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            points INTEGER DEFAULT 0,
            front_photo TEXT,
            back_photo TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# የዳታቤዝ ረዳት ፈንክሽኖች
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT points, front_photo, back_photo FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute('INSERT INTO users (user_id, points) VALUES (?, 2)', (user_id,)) # አዲስ ተጠቃሚ 2 ፍሪ ፖይንት ይሰጠዋል
        conn.commit()
        row = (2, None, None)
    conn.close()
    return {"points": row[0], "front": row[1], "back": row[2]}

def update_user_field(user_id, field, value):
    conn = sqlite3.connect('users.db')
    cursor = cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()

# 2. የፎቶ ማቀናበሪያ (Image Processing) ሎጂክ
def process_id_card(front_path, back_path, output_path):
    """
    የፊት እና የጀርባ ፎቶዎችን ተቀብሎ አቀናጅቶ አንድ ላይ ለህትመት ዝግጁ ያደርጋል
    """
    # መደበኛ የመታወቂያ መጠን ሬሾ (CR80 ID size: 3.370 × 2.125 inches)
    id_width = 1011
    id_height = 638
    
    front = Image.open(front_path).resize((id_width, id_height), Image.Resampling.LANCZOS)
    back = Image.open(back_path).resize((id_width, id_height), Image.Resampling.LANCZOS)
    
    # ባዶ ነጭ ገጽ ማዘጋጀት (A4 መጠን በ 300 DPI አካባቢ)
    canvas_width = 2480
    canvas_height = 3508
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # ፎቶዎቹን መሃል ላይ ማስቀመጥ (የፊት ገጽ ከላይ፣ የጀርባ ገጽ ከበታቹ)
    x_offset = (canvas_width - id_width) // 2
    y_offset_front = 400
    y_offset_back = y_offset_front + id_height + 200 # በፎቶዎቹ መካከል 200px ክፍተት
    
    canvas.paste(front, (x_offset, y_offset_front))
    canvas.paste(back, (x_offset, y_offset_back))
    
    canvas.save(output_path, "PDF", resolution=300.0)

# 3. የቴሌግራም ቦት ትዕዛዞች (Bot Handlers)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    text = (
        "👋 እንኳን ወደ Fayda ID Converter ቦት በሰላም መጡ! \n\n"
        "የዲጂታል መታወቂያዎን ፎቶዎች ወደ ማተሚያ ዝግጁ PDF መቀየር ይችላሉ።\n\n"
        f"💰 የእርስዎ ቀሪ ፖይንት፦ *{user_data['points']} ፖይንት*\n"
        "⚠️ ማስታወሻ፦ 1 መታወቂያ ለመቀየር 1 ፖይንት ይጠይቃል።"
    )
    
    keyboard = [
        [InlineKeyboardButton("🖼️ መታወቂያ ቀይር", callback_data="start_convert")],
        [InlineKeyboardButton("💳 ፖይንት ግዛ / Wallet", callback_data="view_wallet")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = get_user(user_id)
    
    if query.data == "start_convert":
        if user_data['points'] < 1:
            await query.edit_message_text(
                "❌ ይቅርታ፣ በቂ ፖይንት የለዎትም። እባክዎ መጀመሪያ ፖይንት ይግዙ።",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 ፖይንት ግዛ", callback_data="view_wallet")]])
            )
            return
            
        update_user_field(user_id, 'front_photo', None)
        update_user_field(user_id, 'back_photo', None)
        await query.edit_message_text("📸 እባክዎ የመታወቂያውን **የፊት ገጽ (Front)** ፎቶ ይላኩ።")
        
    elif query.data == "view_wallet":
        wallet_text = (
            f"💳 **የሂሳብ መዝገብ (Wallet)**\n\n"
            f"👤 የተጠቃሚ ID: `{user_id}`\n"
            f"🪙 ቀሪ ፖይንት: *{user_data['points']}*\n\n"
            "📌 ፖይንት ለመግዛት በቴሌብር፣ ሲቢኢ ብር መክፈል ይችላሉ።\n"
            "የከፈሉበትን ደረሰኝ (Screenshot) ለአድሚን በመላክ ፖይንት ማስሞላት ይችላሉ።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋና ማውጫ", callback_data="back_to_main")]]
        await query.edit_message_text(wallet_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("🖼️ መታወቂያ ቀይር", callback_data="start_convert")],
            [InlineKeyboardButton("💳 ፖይንት ግዛ / Wallet", callback_data="view_wallet")]
        ]
        await query.edit_message_text(
            f"እንኳን ተመለሱ። ቀሪ ፖይንትዎ፦ *{user_data['points']}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    # ፎቶውን ማውረድ
    photo_file = await update.message.photo[-1].get_file()
    os.makedirs("downloads", exist_ok=True)
    
    if not user_data['front']:
        # የፊት ፎቶ ከሌለ ይህንን እንደ ፊት መመዝገብ
        file_path = f"downloads/{user_id}_front.jpg"
        await photo_file.download_to_drive(file_path)
        update_user_field(user_id, 'front_photo', file_path)
        await update.message.reply_text("🔄 የፊት ገጽ ተቀብያለሁ! አሁን ደግሞ **የጀርባውን ገጽ (Back)** ፎቶ ይላኩ።")
        
    elif user_data['front'] and not user_data['back']:
        # የፊት ፎቶ ኖሮ የጀርባ ከሌለ ይህንን እንደ ጀርባ መመዝገብ
        file_path = f"downloads/{user_id}_back.jpg"
        await photo_file.download_to_drive(file_path)
        update_user_field(user_id, 'back_photo', file_path)
        
        await update.message.reply_text("⏳ ሁለቱንም ፎቶዎች አግኝቻለሁ። ወደ ማተሚያ PDF እየቀየርኩ ነው፣ እባክዎ ጥቂት ሰከንዶች ይጠብቁ...")
        
        # ማቀናበር
        output_pdf = f"downloads/{user_id}_fayda_print.pdf"
        try:
            process_id_card(user_data['front'], file_path, output_pdf)
            
            # ፖይንት መቀነስ
            new_points = user_data['points'] - 1
            update_user_field(user_id, 'points', new_points)
            
            # ፒዲኤፉን መላክ
            with open(output_pdf, 'rb') as doc:
                await update.message.reply_document(
                    document=doc,
                    filename="Fayda_ID_Print_Ready.pdf",
                    caption=f"✅ መታወቂያዎ በተሳካ ሁኔታ ተዘጋጅቷል!\n💰 ቀሪ ፖይንትዎ፦ {new_points}"
                )
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            await update.message.reply_text("❌ ፎቶውን በመቀየር ላይ ስህተት አጋጥሟል። እባክዎ ፎቶዎቹ ጥራት ያላቸው መሆናቸውን ያረጋግጡ።")
            
        # የቆዩ ፋይሎችን ማጽዳት
        update_user_field(user_id, 'front_photo', None)
        update_user_field(user_id, 'back_photo', None)

# 4. የአድሚን ትዕዛዝ (ለተጠቃሚዎች ፖይንት ለመጨመር)
# አጠቃቀም፦ /addpoint USER_ID POINTS (ምሳሌ፦ /addpoint 54321678 10)
async def add_point(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return # አድሚን ካልሆነ ምንም አያደርግም
        
    try:
        target_user = int(context.args[0])
        amount = int(context.args[1])
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT points FROM users WHERE user_id = ?', (target_user,))
        row = cursor.fetchone()
        
        if row:
            new_pts = row[0] + amount
            cursor.execute('UPDATE users SET points = ? WHERE user_id = ?', (new_pts, target_user))
            conn.commit()
            await update.message.reply_text(f"✅ ለተጠቃሚ `{target_user}` {amount} ፖይንት ተጨምሯል። አጠቃላይ፦ {new_pts}")
            # ለተጠቃሚው መልዕክት መላክ
            await context.bot.send_message(chat_id=target_user, text=f"🎉 {amount} ፖይንት በአድሚን ተሞልቶልዎታል! ቀሪ ፖይንትዎ፦ {new_pts}")
        else:
            await update.message.reply_text("❌ ተጠቃሚው በቦቱ ላይ አልተገኘም።")
        conn.close()
    except Exception as e:
        await update.message.reply_text("⚠️ አጠቃቀም ስህተት፦ `/addpoint USER_ID POINTS` በሚል ያስገቡ።")

# 5. የቦት አፕሊኬሽን ማደራጃ
bot_app = Application.builder().token(BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("addpoint", add_point))
bot_app.add_handler(CallbackQueryHandler(button_click))
bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photos))

# 6. የRender ዌብሁክ እና የFlask ራውቲንግ
@app.route("/", methods=["GET"])
def index():
    return "Fayda ID Converter Bot is Running Live!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        await bot_app.initialize()
        await bot_app.process_update(update)
        return "OK", 200

if __name__ == "__main__":
    # ለሎካል መሞከሪያ (Local Testing)
    # bot_app.run_polling()
    
    # ለRender ፕሮዳክሽን
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
