import os
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup

# ক্রেডেনশিয়াল সেটআপ
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("✅ অভিনন্দন! বোটটি অবশেষে সচল হয়েছে।")

# --- কোনো জটিল লুপ ছাড়া সরাসরি রান ---
if __name__ == "__main__":
    print("বোট চালু হচ্ছে...")
    app.run()
