import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply, BotCommand

# --- ১. Flask Server (Render-এর জন্য) ---
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

# ডাটা স্টোরেজ
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

# --- ৩. কমান্ডস এবং স্টার্ট ---
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
    welcome_joke = (
        f"🚀 **Welcome to VCF Pro Worker Bot!** 🚀\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"হ্যালো **{message.from_user.first_name}**, আমি আপনার ফাইল ম্যানেজ করতে রেডি।\n\n"
        f"💡 **একটি মজার জোকস:**\n"
        f"টিচার: বল্টু, বল তো 'পৃথিবী গোল'—এর ইংরেজি কী?\n"
        f"বল্টু: Sir, The Earth is Round.\n"
        f"টিচার: গুড! এবার বল এটা কে আবিষ্কার করেছেন?\n"
        f"বল্টু: স্যার, আমি তো করিনি, ফুটবল খেলতে গিয়ে গোল দিয়েছি শুধু! 😂⚽\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 শুরু করতে নিচের বাটনগুলো ব্যবহার করুন।"
    )
    await message.reply_text(welcome_joke, reply_markup=main_menu)

# --- ৪. Admin Navy ফিচার (আপনার পুরনো লজিক) ---
@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 Masukkan nomor admin:", reply_markup=ForceReply(True))

# --- ৫. ফাইল টু VCF ফিচার ---
@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 দয়া করে আপনার কন্টাক্ট লিস্টের .txt অথবা .xlsx ফাইলটি পাঠান।")

@app.on_message(filters.document)
async def handle_document(client, message):
    # পারমিশন ছাড়াই এখন ফাইল ডাউনলোড হবে
    file_path = await message.download()
    user_data[message.from_user.id] = {'file_path': file_path, 'step': 0}
    await message.reply_text("⚙️ ফাইল পাওয়া গেছে! কনভার্ট শুরু করতে /done লিখুন।")

@app.on_message(filters.command("done"))
async def start_done(client, message):
    uid = message.from_user.id
    if uid in user_data:
        user_data[uid]['step'] = 1
        await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি নাম দিন:", reply_markup=ForceReply(True))

# --- ৬. রিপ্লাই হ্যান্ডলিং (আসল কনভার্টিং লজিক) ---
@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    
    if uid in admin_navy_data:
        data = admin_navy_data[uid]
        step = data["step"]
        if step == 1:
            data["admin_no"] = message.text
            data["step"] = 2
            await message.reply_text("📝 Masukkan nama admin:", reply_markup=ForceReply(True))
        elif step == 2:
            data["admin_name"] = message.text
            data["step"] = 3
            await message.reply_text("🚢 Masukkan nomor navy:", reply_markup=ForceReply(True))
        elif step == 3:
            data["navy_no"] = message.text
            data["step"] = 4
            await message.reply_text("📝 Masukkan nama navy:", reply_markup=ForceReply(True))
        elif step == 4:
            data["navy_name"] = message.text
            data["step"] = 5
            await message.reply_text("📁 Masukkan nama file:", reply_markup=ForceReply(True))
        elif step == 5:
            file_name = message.text
            vcf_content = f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['admin_name']}\nTEL;TYPE=CELL:{data['admin_no']}\nEND:VCARD\n"
            navy_list = data['navy_no'].replace('\n', ' ').split()
            for i, num in enumerate(navy_list):
                vcf_content += f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['navy_name']} {i+1}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n"
            vcf_path = f"{file_name}.vcf"
            with open(vcf_path, "w", encoding='utf-8') as f: f.write(vcf_content)
            await message.reply_document(vcf_path, caption="✅ File সফলভাবে তৈরি হয়েছে!")
            os.remove(vcf_path)
            del admin_navy_data[uid]

async def main():
    async with app:
        await set_bot_commands(app)
        print("Bot is Alive with conversion logic!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    # সার্ভার চালানো হচ্ছে যাতে Render-এ অফ না হয়
    threading.Thread(target=run_server, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
