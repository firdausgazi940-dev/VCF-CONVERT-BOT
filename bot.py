import os
import asyncio
import threading
import pandas as pd
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply, BotCommand

# --- ১. Flask Server সেটআপ (Render-এর স্লিপ মোড ও পোর্ট এরর এড়াতে) ---
server = Flask(__name__)

@server.route('/')
def ping():
    return "Bot is Alive and Running!", 200

def run_server():
    # Render নিজে থেকেই একটি PORT দেয়, না থাকলে ৮০৮০ ব্যবহার হবে
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# --- ২. বোট ক্রেডেনশিয়াল সেটআপ ---
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
# Render-এর Environment Variable থেকে টোকেন নেবে, না থাকলে ডিফল্টটি ব্যবহার করবে
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# ডাটা স্টোরেজ
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
        BotCommand("admin", "অ্যাডমিন নেভি ফিচার"),
        BotCommand("help", "সহায়তা")
    ]
    await client.set_bot_commands(commands)

# --- ৩. বোট লজিক ও হ্যান্ডলার ---

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 স্বাগতম! VCF কনভার্টার বোটে।\nকাজ শুরু করতে নিচের মেনু থেকে **/to_vcf** সিলেক্ট করুন।",
        reply_markup=main_menu
    )

@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 দয়া করে আপনার কন্টাক্ট লিস্টের **.txt** অথবা **.xlsx** ফাইলটি পাঠান।")

@app.on_message(filters.document)
async def handle_document(client, message):
    file_ext = message.document.file_name.split('.')[-1].lower()
    if file_ext in ['txt', 'xlsx']:
        file_path = await message.download()
        user_data[message.from_user.id] = {'file_path': file_path, 'step': 'waiting_for_done'}
        await message.reply_text("✅ ফাইল পাওয়া গেছে। কনভার্ট শুরু করতে **/done** লিখুন।")
    else:
        await message.reply_text("❌ দুঃখিত! শুধু .txt বা .xlsx ফাইল পাঠান।")

@app.on_message(filters.command("done"))
async def done_command(client, message):
    uid = message.from_user.id
    if uid in user_data and user_data[uid]['step'] == 'waiting_for_done':
        user_data[uid]['step'] = 'waiting_for_name'
        await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি নাম দিন (যেমন: Yesss):", reply_markup=ForceReply(True))

# --- অ্যাডমিন নেভি ফিচার ---
@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 অ্যাডমিন নম্বর দিন:", reply_markup=ForceReply(True))

# --- রিপ্লাই হ্যান্ডলিং (সব লজিক এখানে) ---
@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    
    # ১. সাধারণ ফাইল টু VCF লজিক
    if uid in user_data and user_data[uid].get('step') == 'waiting_for_name':
        contact_name = message.text
        file_path = user_data[uid]['file_path']
        await message.reply_text(f"⏳ '{contact_name}' নামে ফাইল প্রসেসিং হচ্ছে...")

        try:
            contacts = []
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                contacts = df.iloc[:, 0].astype(str).tolist()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    contacts = [line.strip() for line in f if line.strip()]

            vcf_name = f"{contact_name}.vcf"
            with open(vcf_name, "w", encoding='utf-8') as f:
                for i, phone in enumerate(contacts):
                    f.write(f"BEGIN:VCARD\nVERSION:3.0\nFN:{contact_name} {i+1}\nTEL;TYPE=CELL:{phone}\nEND:VCARD\n")
            
            await message.reply_document(vcf_name, caption=f"✅ সফলভাবে {len(contacts)}টি কন্টাক্ট কনভার্ট হয়েছে।")
            os.remove(vcf_name)
            os.remove(file_path)
            del user_data[uid]
        except Exception as e:
            await message.reply_text(f"❌ এরর: {str(e)}")
        return

    # ২. অ্যাডমিন নেভি লজিক
    if uid in admin_navy_data:
        data = admin_navy_data[uid]
        step = data["step"]
        if step == 1:
            data["admin_no"] = message.text
            data["step"] = 2
            await message.reply_text("📝 অ্যাডমিন নাম দিন:", reply_markup=ForceReply(True))
        elif step == 2:
            data["admin_name"] = message.text
            data["step"] = 3
            await message.reply_text("🚢 নেভি নম্বর দিন (এক বা একাধিক):", reply_markup=ForceReply(True))
        elif step == 3:
            data["navy_no"] = message.text
            data["step"] = 4
            await message.reply_text("📝 নেভি নাম দিন:", reply_markup=ForceReply(True))
        elif step == 4:
            data["navy_name"] = message.text
            data["step"] = 5
            await message.reply_text("📁 ফাইলের নাম কী হবে?", reply_markup=ForceReply(True))
        elif step == 5:
            file_name = message.text
            vcf_content = f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['admin_name']}\nTEL;TYPE=CELL:{data['admin_no']}\nEND:VCARD\n"
            navy_list = data['navy_no'].replace('\n', ' ').split()
            for i, num in enumerate(navy_list):
                vcf_content += f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['navy_name']} {i+1}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n"
            vcf_path = f"{file_name}.vcf"
            with open(vcf_path, "w", encoding='utf-8') as f: f.write(vcf_content)
            await message.reply_document(vcf_path, caption="✅ অ্যাডমিন নেভি ফাইল তৈরি হয়েছে!")
            os.remove(vcf_path)
            del admin_navy_data[uid]
        return

# --- ৪. মেইন ফাংশন ---
async def main():
    async with app:
        await set_bot_commands(app)
        print("Bot is successfully running...")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    # Flask সার্ভারকে আলাদা থ্রেডে চালানো হচ্ছে
    threading.Thread(target=run_server, daemon=True).start()
    
    # asyncio লুপ সেটআপ
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
