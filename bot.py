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

# স্টোরেজ
user_data = {}
admin_navy_data = {} # Admin Navy প্রসেসের জন্য আলাদা স্টোরেজ

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
        BotCommand("start", "মুল মেনু চালু করুন"),
        BotCommand("to_vcf", "ফাইল থেকে VCF কনভার্ট করুন"),
        BotCommand("admin", "অ্যাডমিন নেভি (নতুন ফিচার)"),
        BotCommand("help", "সহায়তা নিন")
    ]
    await client.set_bot_commands(commands)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 স্বাগতম! VCF কনভার্টার বোটে।", reply_markup=main_menu)

# --- Admin Navy ফিচার শুরু ---
@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 Masukkan nomor admin:", reply_markup=ForceReply(True))

@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    
    # সাধারণ VCF কনভারশন হ্যান্ডলার (আপনার আগের কোড)
    if uid in user_data:
        await process_conversion(client, message)
        return

    # Admin Navy হ্যান্ডলার
    if uid in admin_navy_data:
        step = admin_navy_data[uid]["step"]
        
        if step == 1:
            admin_navy_data[uid]["admin_no"] = message.text
            admin_navy_data[uid]["step"] = 2
            await message.reply_text("📝 Masukkan nama admin:", reply_markup=ForceReply(True))
            
        elif step == 2:
            admin_navy_data[uid]["admin_name"] = message.text
            admin_navy_data[uid]["step"] = 3
            await message.reply_text("🚢 Masukkan nomor navy (পার্থক্য করতে কমা বা স্পেস দিন):", reply_markup=ForceReply(True))
            
        elif step == 3:
            admin_navy_data[uid]["navy_no"] = message.text
            admin_navy_data[uid]["step"] = 4
            await message.reply_text("📝 Masukkan nama navy:", reply_markup=ForceReply(True))
            
        elif step == 4:
            admin_navy_data[uid]["navy_name"] = message.text
            admin_navy_data[uid]["step"] = 5
            await message.reply_text("📁 Masukkan nama file:", reply_markup=ForceReply(True))
            
        elif step == 5:
            file_name = message.text
            data = admin_navy_data[uid]
            
            # VCF ফাইল তৈরি
            vcf_content = ""
            # Admin কন্টাক্ট যোগ
            vcf_content += f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['admin_name']}\nTEL;TYPE=CELL:{data['admin_no']}\nEND:VCARD\n"
            
            # Navy কন্টাক্ট যোগ (একাধিক নম্বর থাকলে প্রসেস করবে)
            navy_list = data['navy_no'].replace('\n', ' ').split()
            for i, num in enumerate(navy_list):
                name = f"{data['navy_name']} {i+1}" if len(navy_list) > 1 else data['navy_name']
                vcf_content += f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n"
            
            vcf_path = f"{file_name}.vcf"
            with open(vcf_path, "w", encoding='utf-8') as f:
                f.write(vcf_content)
            
            await message.reply_document(vcf_path, caption="✅ File berhasil dikirim!")
            os.remove(vcf_path)
            del admin_navy_data[uid]

# --- সাধারণ VCF কনভারশন (অপরিবর্তিত) ---
@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 Send your .txt or .xlsx file")

@app.on_message(filters.document)
async def handle_document(client, message):
    file_path = await message.download()
    user_data[message.from_user.id] = {'file_path': file_path, 'step': 1}
    await message.reply_text("✅ File received! Send `/done` to start.")

async def process_conversion(client, message):
    # আপনার আগের দেওয়া প্রসেসিং লজিক এখানে কাজ করবে
    pass 

# --- মেইন ফাংশন ---
async def main():
    async with app:
        await set_bot_commands(app)
        print("বোট অ্যাডমিন নেভি ফিচারসহ চালু হয়েছে!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    asyncio.run(main())
