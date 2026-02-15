import os
import asyncio
import threading
import pandas as pd
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

# --- ১. Flask Server ---
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

# আপনার QR যুক্ত স্পেশাল ফটোর সরাসরি লিংক
START_PHOTO = "https://graph.org/file/9970860538a7985472855.jpg" 

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

# --- ৩. মেইন কমান্ডস ---

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = (
        "👋 **স্বাগতম! আমি VCF কনভার্টার বোট।**\n\n"
        "👤 **Owner:** `AMG ABDUL`\n"
        "🆔 **Username:** @Helllo68\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "কাজ শুরু করতে নিচের মেনু থেকে অপশন বেছে নিন।"
    )
    try:
        # ফটোসহ স্টার্ট মেসেজ
        await message.reply_photo(
            photo=START_PHOTO,
            caption=welcome_text,
            reply_markup=main_menu
        )
    except Exception as e:
        # ফটো না আসলে শুধু টেক্সট পাঠাবে
        await message.reply_text(welcome_text, reply_markup=main_menu)

# ... (বাকি সব ফাংশন আগের মতোই থাকবে) ...

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

@app.on_message(filters.command("admin"))
async def admin_navy_start(client, message):
    uid = message.from_user.id
    admin_navy_data[uid] = {"step": 1}
    await message.reply_text("👤 অ্যাডমিন নম্বর দিন:", reply_markup=ForceReply(True))

@app.on_message(filters.reply & filters.text)
async def handle_replies(client, message):
    uid = message.from_user.id
    
    if uid in user_data:
        data = user_data[uid]
        if data['step'] == 'ctc_name':
            data['ctc_name'] = message.text
            data['step'] = 'file_name'
            await message.reply_text("💾 এবার ফাইলের জন্য একটি নাম দিন (যেমন: Result):", reply_markup=ForceReply(True))
            return
        elif data['step'] == 'file_name':
            data['file_prefix'] = message.text
            data['step'] = 'limit'
            await message.reply_text("🔢 প্রতি ফাইলে কতগুলো কন্টাক্ট থাকবে? (সবগুলোর জন্য 'all' লিখুন):", reply_markup=ForceReply(True))
            return
        elif data['step'] == 'limit':
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
                total = len(contacts)
                limit = total if limit_text.lower() == 'all' else int(limit_text)
                count = 0; file_num = 1; vcf_buffer = ""
                for i, phone in enumerate(contacts):
                    vcf_buffer += f"BEGIN:VCARD\nVERSION:3.0\nFN:{ctc_name} {i+1}\nTEL;TYPE=CELL:{phone}\nEND:VCARD\n"
                    count += 1
                    if count == limit or i == total - 1:
                        vcf_name = f"{file_prefix}_{file_num}.vcf"
                        with open(vcf_name, "w", encoding='utf-8') as f: f.write(vcf_buffer)
                        await message.reply_document(vcf_name, caption=f"📄 ফাইল নং: {file_num}\n✅ কন্টাক্ট: {count}")
                        os.remove(vcf_name)
                        vcf_buffer = ""; count = 0; file_num += 1
                os.remove(input_file)
                del user_data[uid]
                await message.reply_text("✅ কনভারশন সম্পন্ন হয়েছে!")
            except Exception as e:
                await message.reply_text(f"❌ ভুল হয়েছে: {e}")
            return

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
            await message.reply_document(vcf_path, caption="✅ অ্যাডমিন নেভি ফাইল সফলভাবে তৈরি হয়েছে!")
            os.remove(vcf_path)
            del admin_navy_data[uid]
        return

async def main():
    async with app:
        print("Bot is Alive!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
# --- Multilingual & Premium Support (Pyrogram Version) ---

@app.on_message(filters.command(["start", "language"]))
async def set_language(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")]
    ])
    await message.reply_text(
        "Please select your language / আপনার ভাষা নির্বাচন করুন / अपनी भाषा चुनें:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("^lang_"))
async def handle_language_selection(client, callback_query):
    lang = callback_query.data.split("_")[1]
    messages = {
        "bn": "আপনার ভাষা সেট করা হয়েছে: **বাংলা**।\nফ্রি ট্রায়াল শুরু করতে VCF ফাইল পাঠান। প্রিমিয়ামের জন্য /plan লিখুন।",
        "en": "Language set to: **English**.\nSend your VCF file for a free trial. Type /plan for Premium.",
        "hi": "आपकी भाषा चुनी गई: **हिन्दी**।\nफ्री ट्रायल के लिए VCF फाइल भेजें। प्रीमियम के लिए /plan लिखें।"
    }
    await callback_query.answer("Success!")
    await callback_query.edit_message_text(messages[lang])

@app.on_message(filters.command(["plan", "premium"]))
async def multi_lang_premium(client, message):
    premium_text = (
        "🌟 **Premium Plans** 🌟\n\n"
        "🇧🇩 **বাংলা:** আনলিমিটেড কনভার্ট করতে ₹99 পেমেন্ট করে স্ক্রিনশট দিন: @Helllo68\n\n"
        "🇺🇸 **English:** Pay ₹99 for Unlimited access. Send screenshot to: @Helllo68\n\n"
        "🇮🇳 **हिन्दी:** अनलिमिटेड कन्वर्ट के लिए ₹99 पे करें और स्क्रीनशॉट भेजें: @Helllo68"
    )
    # আপনার কাছে QR কোড থাকলে নিচের লাইনে লিঙ্ক দিন
    # await message.reply_photo("YOUR_QR_LINK", caption=premium_text)
    await message.reply_text(premium_text)

