import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# ==========================================
# 1. MINI WEB SERVER (Khusus untuk Render)
# ==========================================
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot Telegram Gemini Aktif 24/7!"

def run_web_server():
    # Render otomatis memberikan environment variable PORT
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)


# ==========================================
# 2. KONFIGURASI API KEY & MODEL GEMINI
# ==========================================
TELEGRAM_TOKEN = os.getenv("8353700147:AAEGMKN0gPUGXQz4BAgb4IsoYGRKAo1S55U")
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6LG4QhMK9uw_bqCCcZ7Gh9D2wPsoK7bElgFbLwLqaMKdA")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------
# ATUR KEPRIBADIAN, NAMA, DAN PERAN BOT SESUAI KEINGINAN DI SINI
# ---------------------------------------------------------------------
SYSTEM_PROMPT = """
Nama Anda adalah 'Jarvis'.
Anda adalah asisten AI pribadi yang cerdas, ramah, dan serba tahu.
Peran Anda: Membantu pengguna menjawab pertanyaan, memberikan ide koding, dan berdiskusi.
Gaya Bahasa: Bahasa Indonesia yang santai, responsif, sopan, dan mudah dipahami.
Aturan Tambahan: Selalu perkenalkan diri Anda sebagai Jarvis jika pengguna baru menyapa atau meminta Anda memperkenalkan diri.
"""

# Inisialisasi Model Gemini Flash (Cepat & Kuota Gratis Besar)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)


# ==========================================
# 3. FUNGSI HANDLER TELEGRAM
# ==========================================

# Handler untuk perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        # Gemini otomatis merespon perkenalan sesuai SYSTEM_PROMPT
        response = model.generate_content("Tolong perkenalkan diri kamu secara singkat kepada pengguna!")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Halo! Saya adalah bot AI Anda. Ada yang bisa saya bantu?")
        print(f"Error /start: {e}")

# Handler untuk pesan teks masuk
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Tampilkan status "typing..." di aplikasi Telegram
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Kirim pesan ke Gemini
        response = model.generate_content(user_text)
        reply_text = response.text

        # Batas maksimal pesan Telegram adalah 4096 karakter
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                await update.message.reply_text(reply_text[i:i+4000])
        else:
            await update.message.reply_text(reply_text)

    except Exception as e:
        await update.message.reply_text("Maaf, terjadi kesalahan saat memproses jawaban.")
        print(f"Error: {e}")


# ==========================================
# 4. JALANKAN APLIKASI
# ==========================================
if __name__ == "__main__":
    # Jalankan web server di background thread
    threading.Thread(target=run_web_server, daemon=True).start()

    print("Bot Telegram Gemini sedang berjalan...")
    
    # Inisialisasi Bot Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Daftarkan Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Mulai polling pesan dari Telegram
    app.run_polling()
