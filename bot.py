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

# মেইন মেনু কিবোর্ড
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
    await message.reply_text("👋 স্বাগতম! VCF কনভার্টার বোটে।\n\nবোটটি বর্তমানে **Docker** মোডে সফলভাবে সচল আছে।", reply_markup=main_menu)

# --- Admin Navy ফিচার ---
@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 Masukkan nomor admin:", reply_markup=ForceReply(True))

# --- ফাইল টু VCF ফিচার ---
@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 দয়া করে আপনার কন্টাক্ট লিস্টের .txt অথবা .xlsx ফাইলটি পাঠান।")

@app.on_message(filters.document)
async def handle_document(client, message):
    file_path = await message.download()
    user_data[message.from_user.id] = {'file_path': file_path, 'step': 0}
    await message.reply_text("✅ ফাইল পাওয়া গেছে। কনভার্ট শুরু করতে টাইপ করুন: /done")

@app.on_message(filters.command("done"))
async def start_done(client, message):
    uid = message.from_user.id
    if uid in user_data:
        user_data[uid]['step'] = 1
        await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি নাম দিন:", reply_markup=ForceReply(True))

# --- সব রিপ্লাই হ্যান্ডলিং লজিক ---
@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    
    # ১. Admin Navy লজিক
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
            await message.reply_document(vcf_path, caption="✅ File berhasil dikirim!")
            os.remove(vcf_path)
            del admin_navy_data[uid]
        return

    # ২. ফাইল টু VCF লজিক
    if uid in user_data and user_data[uid].get('step', 0) > 0:
        data = user_data[uid]
        if data['step'] == 1:
            data['ctc_name'] = message.text
            data['step'] = 2
            await message.reply_text("💾 এবার ফাইলের জন্য একটি নাম দিন:", reply_markup=ForceReply(True))
        elif data['step'] == 2:
            data['file_name'] = message.text
            data['step'] = 3
            await message.reply_text("🔢 লিমিট দিন (যেমন: 200 বা all):", reply_markup=ForceReply(True))
        elif data['step'] == 3:
            # এখানে কনভারশন প্রসেস হবে (আগের মতো)
            await message.reply_text("⏳ Processing...")
            # ... (কনভারশন কোড) ...
            del user_data[uid]
        return

async def main():
    async with app:
        await set_bot_commands(app)
        print("বোট ডকার এনভায়রনমেন্টে চালু হয়েছে!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    asyncio.run(main())
