import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# --- ১. Flask Server ---
server = Flask(__name__)

@server.route('/')
def ping():
    return "Bot is Running!", 200

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

# --- ২. বোট ক্রেডেনশিয়াল ---
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

main_menu = ReplyKeyboardMarkup(
    [
        ["/to_vcf", "/to_txt", "/admin", "/manual"],
        ["/add", "/delete", "/renamectc", "/renamefile"],
        ["/merge", "/split", "/count", "/nodup"],
        ["/status", "/vip", "/referral", "/help"]
    ],
    resize_keyboard=True
)

# --- ৩. ভাষা সেটআপ ---

@app.on_message(filters.command(["language", "lang"]))
async def set_language(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")]
    ])
    await message.reply_text("✨ **Select Your Language** ✨\n\nনিচ থেকে আপনার ভাষা বেছে নিন:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^lang_"))
async def handle_language_selection(client, callback_query):
    lang = callback_query.data.split("_")[1]
    msgs = {
        "bn": "✅ **সফল হয়েছে!** ভাষা: বাংলা।\nএখন আপনি যেকোনো ফাইল পাঠিয়ে কাজ শুরু করতে পারেন।",
        "en": "✅ **Success!** Language: English.\nYou can now start by sending your files.",
        "hi": "✅ **सफलता!** भाषा: हिन्दी।\nअब आप अपनी फाइलें भेजकर शुरू कर सकते हैं।"
    }
    await callback_query.edit_message_text(msgs[lang])

# --- ৪. মেইন প্রসেস (পারমিশন রিমুভ করা হয়েছে) ---

@app.on_message(filters.command("start"))
async def start(client, message):
    # সুন্দর ওয়েলকাম মেসেজ ও জোকস
    welcome_msg = (
        f"🚀 **Welcome to VCF Pro Worker Bot!** 🚀\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"হ্যালো **{message.from_user.first_name}**, আমি আপনাকে VCF এবং TXT ফাইল ম্যানেজ করতে সাহায্য করব।\n\n"
        f"💡 **একটি ছোট হাসি:**\n"
        f"টিচার: বল্টু, বল তো 'পৃথিবী গোল'—এটার ইংরেজি কী?\n"
        f"বল্টু: Sir, The Earth is Round.\n"
        f"টিচার: গুড! এবার বল তো এটা কে আবিষ্কার করেছেন?\n"
        f"বল্টু: স্যার, আমি তো করিনি, ফুটবল খেলতে গিয়ে গোল দিয়েছি শুধু! 😂⚽\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 **শুরু করতে নিচের বাটন ব্যবহার করুন অথবা ভাষা সেট করুন:** /language"
    )
    # ফটো ছাড়াই টেক্সট পাঠানো হচ্ছে যাতে কোনো এরর না আসে
    await message.reply_text(welcome_msg, reply_markup=main_menu)

@app.on_message(filters.document)
async def handle_document(client, message):
    # এখানে পারমিশন চেক (check_access) সরিয়ে দেওয়া হয়েছে
    await message.reply_text("⚙️ **ফাইল পাওয়া গেছে!** প্রসেসিং শুরু হচ্ছে, দয়া করে অপেক্ষা করুন...")

@app.on_message(filters.command(["plan", "premium"]))
async def show_plan(client, message):
    plan_text = (
        "🌟 **Premium Plans (Optional Support)** 🌟\n\n"
        "বোটটি সবার জন্য উন্মুক্ত! তবে আপনি চাইলে আমাদের সাপোর্ট করতে পারেন।\n"
        "💰 **Price:** ₹99 / $1.5\n"
        "📸 স্ক্রিনশট দিন: @Helllo68\n\n"
        "ধন্যবাদ আমাদের সাথে থাকার জন্য! ❤️"
    )
    await message.reply_text(plan_text)

async def main():
    async with app:
        print("Bot is Alive without Permissions!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    # Render পোর্ট বাইন্ডিং
    threading.Thread(target=run_server, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
