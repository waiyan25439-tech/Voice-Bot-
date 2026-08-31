import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import edge_tts

# GitHub Secrets မှ Bot Token ကို ယူသုံးမည်
TELEGRAM_BOT_TOKEN = os.environ.get("8911235831:AAGjtn3bDHzhR1c5FGbU0MjUKxlBE3R3Q-Y")

VOICE = "my-MM-ThihaNeural"

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
        "စာလုံးရေ ၅,၀၀၀ အထိ ပို့ပေးနိုင်ပြီး MP3 ဖိုင်အနေဖြင့် Save to Downloads ပြုလုပ်နိုင်ပါသည်။"
    )

async def text_to_speech_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if len(text) > 5000:
        await update.message.reply_text(f"⚠️ စာလုံးရေ ၅,၀၀၀ အောက်ထိ လျှော့ပေးပါ (လက်ရှိ: {len(text)} လုံး)။")
        return

    status_msg = await update.message.reply_text("⏳ စာသားများကို အမျိုးသားအသံဖိုင် ပြုလုပ်နေပါသည်...")

    try:
        text_chunks = split_text(text, max_length=2000)
        
        for index, chunk in enumerate(text_chunks):
            file_name = f"Voice_Part_{index + 1}.mp3"
            
            communicate = edge_tts.Communicate(chunk, VOICE)
            await communicate.save(file_name)

            with open(file_name, "rb") as audio_file:
                await update.message.reply_document(
                    document=audio_file,
                    filename=f"Myanmar_Male_Voice_Part_{index + 1}.mp3",
                    caption=f"🔊 မြန်မာအမျိုးသားအသံ အပိုင်း ({index + 1}/{len(text_chunks)})"
                )
            
            if os.path.exists(file_name):
                os.remove(file_name)

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ အမှားတစ်ခု ဖြစ်ပေါ်ခဲ့ပါသည်: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech_handler))

    print("Bot starting on GitHub...")
    app.run_polling()
