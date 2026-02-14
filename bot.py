import os
import asyncio
import threading
import pandas as pd
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply, BotCommand

# --- ১. Flask Server (Render এর জন্য) ---
server = Flask(__name__)

@server.route('/')
def ping():
    return "Bot is Running!", 200

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# --- ২. বোট ক্রেডেনশিয়াল ---
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_data = {}
admin_navy_data = {}

# মেইন মেনু
main_menu = ReplyKeyboardMarkup(
    [
        ["/to_vcf", "/to_txt", "/admin", "/manual"],
        ["/add", "/delete", "/renamectc", "/renamefile"],
        ["/merge", "/split", "/count", "/nodup"],
        ["/status", "/vip", "/referral", "/help"]
    ],
    resize_keyboard=True
)

# --- ৩. মেইন ফাংশনালিটি ---

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 স্বাগতম! VCF কনভার্টার বোটে।\nকাজ শুরু করতে মেনু থেকে **/to_vcf** সিলেক্ট করুন।", reply_markup=main_menu)

@app.on_message(filters.command("to_vcf"))
async def ask_file(client, message):
    await message.reply_text("📩 কন্টাক্ট লিস্টের **.txt** অথবা **.xlsx** ফাইলটি পাঠান।")

@app.on_message(filters.document)
async def handle_document(client, message):
    file_ext = message.document.file_name.split('.')[-1].lower()
    if file_ext in ['txt', 'xlsx']:
        file_path = await message.download()
        user_data[message.from_user.id] = {'file_path': file_path, 'step': 'waiting_for_done'}
        await message.reply_text("✅ ফাইল পাওয়া গেছে। কনভার্ট শুরু করতে **/done** লিখুন।")
    else:
        await message.reply_text("❌ শুধু .txt বা .xlsx ফাইল পাঠান।")

@app.on_message(filters.command("done"))
async def done_command(client, message):
    uid = message.from_user.id
    if uid in user_data:
        user_data[uid]['step'] = 'ctc_name'
        await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি **নাম** দিন (যেমন: MyContact):", reply_markup=ForceReply(True))

# --- অ্যাডমিন নেভি ফিচার ---
@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 অ্যাডমিন নম্বর দিন:", reply_markup=ForceReply(True))

# --- রিপ্লাই হ্যান্ডলিং (নাম, ফাইল নাম ও লিমিট) ---
@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    
    # ১. ফাইল টু VCF এর ধাপগুলো
    if uid in user_data:
        data = user_data[uid]
        if data['step'] == 'ctc_name':
            data['ctc_name'] = message.text
            data['step'] = 'file_name'
            await message.reply_text("💾 এবার ফাইলের জন্য একটি নাম দিন (যেমন: Result):", reply_markup=ForceReply(True))
            return
        
        if data['step'] == 'file_name':
            data['file_prefix'] = message.text
            data['step'] = 'limit'
            await message.reply_text("🔢 প্রতি ফাইলে কতগুলো কন্টাক্ট থাকবে? (সবগুলোর জন্য 'all' লিখুন):", reply_markup=ForceReply(True))
            return

        if data['step'] == 'limit':
            limit_text = message.text
            input_file = data['file_path']
            ctc_name = data['ctc_name']
            file_prefix = data['file_prefix']
            
            await message.reply_text("⏳ ফাইল প্রসেসিং হচ্ছে...")

            try:
                contacts = []
                if input_file.endswith('.txt'):
                    with open(input_file, 'r', encoding='utf-8') as f:
                        contacts = [line.strip() for line in f if line.strip()]
                else:
                    df = pd.read_excel(input_file)
                    contacts = df.iloc[:, 0].astype(str).tolist()

                limit = len(contacts) if limit_text.lower() == 'all' else int(limit_text)
                
                count = 0
                file_num = 1
                vcf_buffer = ""
                
                for i, phone in enumerate(contacts):
                    vcf_buffer += f"BEGIN:VCARD\nVERSION:3.0\nFN:{ctc_name} {i+1}\nTEL;TYPE=CELL:{phone}\nEND:VCARD\n"
                    count += 1
                    
                    if count == limit or i == len(contacts) - 1:
                        vcf_name = f"{file_prefix}_{file_num}.vcf"
                        with open(vcf_name, "w", encoding='utf-8') as f:
                            f.write(vcf_buffer)
                        await message.reply_document(vcf_name, caption=f"📄 ফাইল নং: {file_num}\n✅ কন্টাক্ট সংখ্যা: {count}")
                        os.remove(vcf_name)
                        vcf_buffer = ""; count = 0; file_num += 1

                os.remove(input_file)
                del user_data[uid]
                await message.reply_text("✅ কনভারশন সম্পন্ন হয়েছে!")
            except Exception as e:
                await message.reply_text(f"❌ ভুল হয়েছে: {e}")
            return

    # ২. অ্যাডমিন নেভি লজিক
    if uid in admin_navy_data:
        # (আগের অ্যাডমিন নেভি লজিক এখানে থাকবে...)
        pass

# --- বোট রান ---
async def main():
    async with app:
        print("Bot Started!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
