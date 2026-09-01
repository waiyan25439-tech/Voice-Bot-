import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import edge_tts

TELEGRAM_BOT_TOKEN = "8911235831:AAGjtn3bDHzhR1c5FGbU0MjUKxlBE3R3Q-Y"
VOICE = "my-MM-ThihaNeural"

# User တစ်ယောက်ချင်းစီရဲ့ ခေတ္တစာသား သိမ်းဆည်းရန် Dictionary
user_texts = {}

def split_text(text, max_length=2000):
    words = text.split(' ')
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "မင်္ဂလာပါ! မြန်မာစာသားများကို အမျိုးသားအသံဖြင့် အသံဖိုင်ပြောင်းပေးသော Bot ဖြစ်ပါသည်။\n\n"
        "စာသားပို့ပြီးပါက အသံမြန်နှုန်း (Speed 1x, 2x, 3x) ရွေးချယ်နိုင်ပါသည်။"
    )

# စာသားလက်ခံပြီး Speed ရွေးရန် Button ပြသပေးသည့် Function
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if len(text) > 5000:
        await update.message.reply_text(f"⚠️ စာလုံးရေ ၅,၀၀၀ အောက်ထိ လျှော့ပေးပါ (လက်ရှိ: {len(text)} လုံး)။")
        return

    # User ပို့လိုက်သည့် စာကို ခေတ္တသိမ်းဆည်းခြင်း
    user_texts[user_id] = text

    # Speed ရွေးရန် Button များ ဖန်တီးခြင်း
    keyboard = [
        [
            InlineKeyboardButton("1x (Normal)", callback_data="speed_+0%"),
            InlineKeyboardButton("1.5x", callback_data="speed_+50%"),
        ],
        [
            InlineKeyboardButton("2x", callback_data="speed_+100%"),
            InlineKeyboardButton("3x", callback_data="speed_+200%"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("🔊 အသံမြန်နှုန်း (Speed) ကို ရွေးချယ်ပေးပါ:", reply_markup=reply_markup)

# Button နှိပ်လိုက်ပါက အသံဖိုင် စတင်ထုတ်လုပ်ပေးသည့် Function
async def speed_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    speed_rate = query.data.replace("speed_", "") # ဥပမာ - "+0%", "+100%"

    if user_id not in user_texts:
        await query.edit_message_text("❌ စာသား အချိန်ကျော်လွန်သွားပါပြီ။ စာသား ပြန်ပို့ပေးပါ။")
        return

    text = user_texts[user_id]
    await query.edit_message_text("⏳ အသံဖိုင် ပြုလုပ်နေပါသည်...")

    try:
        text_chunks = split_text(text, max_length=2000)
        
        for index, chunk in enumerate(text_chunks):
            file_name = f"Voice_Part_{index + 1}.mp3"
            
            # edge-tts တွင် rate သတ်မှတ်၍ အသံမြန်နှုန်း ပြောင်းလဲခြင်း
            communicate = edge_tts.Communicate(chunk, VOICE, rate=speed_rate)
            await communicate.save(file_name)

            with open(file_name, "rb") as audio_file:
                await query.message.reply_document(
                    document=audio_file,
                    filename=f"Myanmar_Voice_Speed_{speed_rate.replace('+', '')}_Part_{index + 1}.mp3",
                    caption=f"🔊 မြန်မာအမျိုးသားအသံ (Speed: {speed_rate}) - အပိုင်း ({index + 1}/{len(text_chunks)})"
                )
            
            if os.path.exists(file_name):
                os.remove(file_name)

        # သုံးပြီးသား စာသားကို ခေတ္တသိမ်းထားသည့်နေရာမှ ဖျက်ခြင်း
        del user_texts[user_id]

    except Exception as e:
        await query.message.reply_text(f"❌ အမှားတစ်ခု ဖြစ်ပေါ်ခဲ့ပါသည်: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(speed_button_handler))

    print("Bot starting on GitHub...")
    app.run_polling()
