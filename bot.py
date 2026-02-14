import os
import asyncio
import pandas as pd
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply, BotCommand

# ক্রেডেনশিয়াল সেটআপ
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_data = {}
admin_navy_data = {}

# মেনু কিবোর্ড
main_menu = ReplyKeyboardMarkup(
    [
        ["/to_vcf", "/to_txt", "/admin", "/manual"],
        ["/add", "/delete", "/renamectc", "/renamefile"],
        ["/merge", "/split", "/count", "/nodup"],
        ["/status", "/vip", "/referral", "/help"]
    ],
    resize_keyboard=True
)

async def set_bot_commands(client):
    commands = [
        BotCommand("start", "মূল মেনু"),
        BotCommand("to_vcf", "ফাইল থেকে VCF"),
        BotCommand("admin", "Admin Navy ফিচার"),
        BotCommand("help", "সহায়তা")
    ]
    await client.set_bot_commands(commands)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 স্বাগতম! VCF কনভার্টার বোটে।", reply_markup=main_menu)

# --- Admin Navy ফিচার ---
@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 Masukkan nomor admin:", reply_markup=ForceReply(True))

# --- ফাইল টু VCF ফিচার ---
@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 Send your .txt or .xlsx file")

@app.on_message(filters.document)
async def handle_document(client, message):
    file_path = await message.download()
    user_data[message.from_user.id] = {'file_path': file_path, 'step': 0}
    await message.reply_text("✅ File received! Send `/done` to start.")

@app.on_message(filters.command("done"))
async def start_done(client, message):
    uid = message.from_user.id
    if uid in user_data:
        user_data[uid]['step'] = 1
        await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি নাম দিন:", reply_markup=ForceReply(True))

# --- সব রিপ্লাই হ্যান্ডলিং ---
@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    # Admin Navy লজিক এবং VCF লজিক এখানে থাকবে (আগের কোডের মতো)
    # আমি সংক্ষেপ করছি, আপনি আগের পূর্ণাঙ্গ লজিকটি এখানে রাখবেন।
    pass

# --- মেইন ফাংশন (এরর সমাধানের অংশ) ---
async def start_bot():
    async with app:
        await set_bot_commands(app)
        print("বোট সচল হয়েছে এবং মেনু সেটআপ হয়েছে!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    try:
        # এটি RuntimeError এড়াতে সাহায্য করবে
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Bot Stopped: {e}")
