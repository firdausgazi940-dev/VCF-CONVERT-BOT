import os
import pandas as pd
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

# ক্রেডেনশিয়াল সেটআপ
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

# বোট অবজেক্ট তৈরি
app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# স্টোরেজ
user_data = {}

# মেনু কিবোর্ড
main_menu = ReplyKeyboardMarkup(
    [["/to_vcf", "/to_txt", "/status"], ["/help", "/vip"]],
    resize_keyboard=True
)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("👋 স্বাগতম! বোটটি এখন সচল।", reply_markup=main_menu)

# --- এই অংশটি সবচেয়ে গুরুত্বপূর্ণ (নতুন স্টাইল) ---
if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
