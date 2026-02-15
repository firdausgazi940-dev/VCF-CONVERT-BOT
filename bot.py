import os
import asyncio
import threading
import datetime
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply, BotCommand

# --- ১. Flask Server (Render এর জন্য) ---
server = Flask(__name__)
@server.route('/')
def ping(): return "Bot is Running!", 200

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

# --- ২. বোট ক্রেডেনশিয়াল ---
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")
app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_data = {}
admin_navy_data = {}
VIP_USERS = {}
REFERRALS = {}

# মেইন মেনু কিবোর্ড
main_menu = ReplyKeyboardMarkup(
    [["/to_vcf", "/to_txt", "/admin", "/manual"], 
     ["/add", "/delete", "/renamectc", "/renamefile"], 
     ["/merge", "/split", "/count", "/nodup"], 
     ["/status", "/vip", "/referral", "/help"]],
    resize_keyboard=True
)

# --- ৩. মেইন ফাংশনালিটি (Split Logic সহ) ---

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_msg = f"🚀 **VCF Pro Worker**\nহ্যালো **{message.from_user.first_name}**! শুরু করতে নিচের মেনু ব্যবহার করুন।"
    await message.reply_text(welcome_msg, reply_markup=main_menu)

@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 কন্টাক্ট লিস্টের .txt ফাইলটি পাঠান।")

@app.on_message(filters.document)
async def handle_document(client, message):
    file_path = await message.download()
    user_data[message.from_user.id] = {'file_path': file_path, 'step': 1}
    await message.reply_text("⚙️ ফাইল পাওয়া গেছে! কনভার্ট করতে /done লিখুন।")

@app.on_message(filters.command("done"))
async def start_done(client, message):
    uid = message.from_user.id
    if uid in user_data:
        user_data[uid]['step'] = 2
        await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি নাম দিন (যেমন: MyContact):", reply_markup=ForceReply(True))

@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    
    # VCF splitting logic
    if uid in user_data:
        data = user_data[uid]
        if data['step'] == 2:
            data['contact_name'] = message.text
            data['step'] = 3
            await message.reply_text("🔢 প্রতি ফাইলে কতগুলো কন্টাক্ট থাকবে? (সবগুলোর জন্য 'all' লিখুন):", reply_markup=ForceReply(True))
            return
        
        elif data['step'] == 3:
            try:
                input_val = message.text.lower()
                contact_name = data['contact_name']
                file_path = data['file_path']
                
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]

                total = len(lines)
                limit = total if input_val == 'all' else int(input_val)
                
                await message.reply_text(f"⏳ ফাইল প্রসেসিং হচ্ছে...")

                for i in range(0, total, limit):
                    chunk = lines[i:i + limit]
                    part_no = (i // limit) + 1
                    vcf_filename = f"{contact_name}_{part_no}.vcf" #
                    
                    with open(vcf_filename, "w", encoding="utf-8") as vcf:
                        for idx, num in enumerate(chunk):
                            vcf.write(f"BEGIN:VCARD\nVERSION:3.0\nFN:{contact_name} {i + idx + 1}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n")
                    
                    # ফাইল পাঠানোর সময় সুন্দর ক্যাপশন
                    caption = f"📄 ফাইল নং: {part_no}\n✅ কন্টাক্ট: {len(chunk)}"
                    await message.reply_document(vcf_filename, caption=caption)
                    os.remove(vcf_filename)

                os.remove(file_path)
                del user_data[uid]
                await message.reply_text("✨ সব ফাইল পাঠানো শেষ!")
            except ValueError:
                await message.reply_text("❌ দয়া করে সংখ্যা লিখুন অথবা 'all' লিখুন।")
            return

    # Admin Navy Logic (আপনার পুরনো লজিক এখানে থাকবে)
    # ... (ইতোপূর্বে দেওয়া admin_navy কোডটি এখানে বসাতে পারেন)

if __name__ == "__main__":
    # Render এ বোট সচল রাখতে Flask চালানো হচ্ছে
    threading.Thread(target=run_server, daemon=True).start()
    app.run()
