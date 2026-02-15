import os
import asyncio
import threading
import pandas as pd
import datetime
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton

# --- ১. Flask Server ---
server = Flask(__name__)

@server.route('/')
def ping():
    return "Bot is Running!", 200

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# --- ২. বোট ক্রেডেনশিয়াল ---
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

START_PHOTO = "https://graph.org/file/9970860538a7985472855.jpg" 

# --- ৩. সাবস্ক্রিপশন ডাটাবেস (মেমোরিতে থাকবে) ---
USER_SUBSCRIPTIONS = {} 

user_data = {}
admin_navy_data = {}

main_menu = ReplyKeyboardMarkup(
    [
        ["/to_vcf", "/to_txt", "/admin", "/manual"],
        ["/add", "/delete", "/renamectc", "/renamefile"],
        ["/merge", "/split", "/count", "/nodup"],
        ["/status", "/vip", "/referral", "/help"]
    ],
    resize_keyboard=True
)

# --- ৪. সাবস্ক্রিপশন চেক ফাংশন ---
async def check_access(user_id):
    today = datetime.date.today()
    if user_id in USER_SUBSCRIPTIONS:
        expiry = datetime.datetime.strptime(USER_SUBSCRIPTIONS[user_id], '%Y-%m-%d').date()
        if today <= expiry:
            return True
    return False

# --- ৫. ভাষা ও প্রিমিয়াম কমান্ডস ---

@app.on_message(filters.command(["language", "lang"]))
async def set_language(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")]
    ])
    await message.reply_text("Select Language / ভাষা নির্বাচন করুন:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^lang_"))
async def handle_language_selection(client, callback_query):
    lang = callback_query.data.split("_")[1]
    msgs = {
        "bn": "✅ ভাষা: বাংলা।\nফাইলের কাজ শুরু করতে ১ মাসের প্রিমিয়াম নিন (/plan)।",
        "en": "✅ Language: English.\nGet 1 month premium to start (/plan).",
        "hi": "✅ भाषा: हिन्दी।\nकाम शुरू करने के लिए 1 महीने का प्रीमियम लें (/plan)।"
    }
    await callback_query.edit_message_text(msgs[lang])

@app.on_message(filters.command(["plan", "premium"]))
async def show_plan(client, message):
    joke = "Teacher: 'I am going to school' - ইসকা বাংলা বাতাও।\nBoltu: 'আরে ভাই আমি তো স্কুলে যাচ্ছি, তুই চিল্লাচ্ছিস কেন?' 😂"
    plan_text = (
        f"🌟 **1 Month Premium Plan** 🌟\n\n"
        "💰 **Price:** ₹99 / $1.5\n"
        "📸 পেমেন্ট করে স্ক্রিনশট দিন: @Helllo68\n\n"
        "--- মজার জোকস ---\n" + joke
    )
    await message.reply_photo(photo=START_PHOTO, caption=plan_text)

# অ্যাডমিন হিসেবে আপনি ইউজার যোগ করবেন: /add_user 12345678
@app.on_message(filters.command("add_user") & filters.user("Helllo68"))
async def add_premium(client, message):
    try:
        target_id = int(message.text.split()[1])
        expiry = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        USER_SUBSCRIPTIONS[target_id] = expiry
        await message.reply_text(f"✅ User {target_id} added for 30 days! Expire: {expiry}")
    except:
        await message.reply_text("Usage: /add_user USER_ID")

# --- ৬. মেইন প্রসেস (অ্যাক্সেস চেক সহ) ---

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = "👋 স্বাগতম! কাজ শুরু করতে আগে ভাষা সেট করুন: /language"
    await message.reply_photo(photo=START_PHOTO, caption=welcome_text, reply_markup=main_menu)

@app.on_message(filters.document)
async def handle_document(client, message):
    user_id = message.from_user.id
    if await check_access(user_id):
        # আপনার কনভার্ট লজিক এখানে চলবে
        await message.reply_text("✅ Premium Active! Processing file...")
    else:
        await message.reply_text("🚫 অ্যাক্সেস নেই! ১ মাসের সাবস্ক্রিপশন নিতে /plan দেখুন।")

# ... [বাকি সব ফাংশন যা আপনার আগে ছিল] ...

async def main():
    async with app:
        print("Bot is Alive!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
