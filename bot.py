import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply, BotCommand

# --- ১. Flask Server ---
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

main_menu = ReplyKeyboardMarkup(
    [["/to_vcf", "/to_txt", "/admin", "/manual"], ["/add", "/delete", "/renamectc", "/renamefile"], ["/merge", "/split", "/count", "/nodup"], ["/status", "/vip", "/referral", "/help"]],
    resize_keyboard=True
)

# --- ৩. কমান্ডস ---
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"🚀 **VCF Pro Worker**\nহ্যালো **{message.from_user.first_name}**! শুরু করুন।", reply_markup=main_menu)

@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    # অন্য সব প্রসেস ক্লিন করে শুধু অ্যাডমিন প্রসেস শুরু করা
    if uid in user_data: del user_data[uid]
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 **অ্যাডমিন নম্বরটি দিন:**\n(রিপ্লাই হিসেবে টাইপ করুন)", reply_markup=ForceReply(True))

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
        await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি **নাম** দিন:", reply_markup=ForceReply(True))

# --- ৪. স্পেশাল রিপ্লাই হ্যান্ডলার ---
@app.on_message(filters.reply & filters.text & ~filters.command(["start", "admin", "done", "to_vcf"]))
async def handle_replies(client, message):
    uid = message.from_user.id
    text = message.text

    # ১. Admin Navy লজিক (এটি এখন অগ্রাধিকার পাবে)
    if uid in admin_navy_data:
        step = admin_navy_data[uid]["step"]
        
        if step == 1:
            admin_navy_data[uid]["admin_no"] = text
            admin_navy_data[uid]["step"] = 2
            await message.reply_text("📝 **অ্যাডমিন নাম দিন:**", reply_markup=ForceReply(True))
        elif step == 2:
            admin_navy_data[uid]["admin_name"] = text
            admin_navy_data[uid]["step"] = 3
            await message.reply_text("🚢 **নেভি নম্বরগুলো দিন (স্পেস দিয়ে):**", reply_markup=ForceReply(True))
        elif step == 3:
            admin_navy_data[uid]["navy_no"] = text
            admin_navy_data[uid]["step"] = 4
            await message.reply_text("📝 **নেভি নাম দিন:**", reply_markup=ForceReply(True))
        elif step == 4:
            admin_navy_data[uid]["navy_name"] = text
            admin_navy_data[uid]["step"] = 5
            await message.reply_text("📁 **ফাইলের নাম কী হবে?:**", reply_markup=ForceReply(True))
        elif step == 5:
            data = admin_navy_data[uid]
            vcf_content = f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['admin_name']}\nTEL;TYPE=CELL:{data['admin_no']}\nEND:VCARD\n"
            navy_list = data['navy_no'].replace('\n', ' ').split()
            for i, num in enumerate(navy_list):
                vcf_content += f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['navy_name']} {i+1}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n"
            
            vcf_path = f"{text}.vcf"
            with open(vcf_path, "w", encoding='utf-8') as f: f.write(vcf_content)
            await message.reply_document(vcf_path, caption="✅ Admin Navy ফাইল রেডি!")
            os.remove(vcf_path)
            del admin_navy_data[uid]
        return

    # ২. সাধারণ VCF Split লজিক
    if uid in user_data:
        step = user_data[uid]["step"]
        if step == 2:
            user_data[uid]['contact_name'] = text
            user_data[uid]['step'] = 3
            await message.reply_text("🔢 **প্রতি ফাইলে কতগুলো কন্টাক্ট থাকবে?**\n(যেমন: 1000)", reply_markup=ForceReply(True))
        elif step == 3:
            try:
                limit = int(text)
                contact_name = user_data[uid]['contact_name']
                file_path = user_data[uid]['file_path']
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                for i in range(0, len(lines), limit):
                    chunk = lines[i:i + limit]
                    vcf_fn = f"{contact_name}_{ (i//limit)+1 }.vcf"
                    with open(vcf_fn, "w", encoding="utf-8") as vcf:
                        for idx, num in enumerate(chunk):
                            vcf.write(f"BEGIN:VCARD\nVERSION:3.0\nFN:{contact_name} {i+idx+1}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n")
                    await message.reply_document(vcf_fn, caption=f"📄 পার্ট: {(i//limit)+1}\n✅ কন্টাক্ট: {len(chunk)}")
                    os.remove(vcf_fn)
                os.remove(file_path)
                del user_data[uid]
            except:
                await message.reply_text("❌ শুধু সংখ্যা দিন।")
        return

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    app.run()
