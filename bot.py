import os
import asyncio
import pandas as pd
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

# ক্রেডেনশিয়াল সেটআপ
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_data = {}

main_menu = ReplyKeyboardMarkup(
    [["/to_vcf", "/to_txt", "/status"], ["/help", "/vip"]],
    resize_keyboard=True
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("✅ বোট সচল হয়েছে! কাজ শুরু করতে /to_vcf দিন।", reply_markup=main_menu)

@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 ফাইল পাঠান (.txt বা .xlsx)")

# --- বোট রান করার আধুনিক পদ্ধতি (Python 3.10 এর জন্য) ---
if __name__ == "__main__":
    print("বোট স্টার্ট হচ্ছে...")
    app.run()
