
import os
import asyncio
import pandas as pd
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

# ক্রেডেনশিয়াল সেটআপ
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
# Render Environment Variable থেকে টোকেন নেবে
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# স্টোরেজ (টেম্পোরারি ডাটা রাখার জন্য)
user_data = {}

# মেনু কিবোর্ড
main_menu = ReplyKeyboardMarkup(
    [
        ["/to_vcf", "/to_txt", "/admin", "/manual"],
        ["/add", "/delete", "/renamectc", "/renamefile"],
        ["/merge", "/split", "/count", "/nodup"],
        ["/getname", "/generate", "/getconten", "/setting"],
        ["/status", "/vip", "/referral", "/help"]
    ],
    resize_keyboard=True
)

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
        user_data[message.from_user.id] = {'file_path': file_path}
        await message.reply_text("✅ ফাইল পাওয়া গেছে। কনভার্ট শুরু করতে টাইপ করুন: `/done`")
    else:
        await message.reply_text("❌ দুঃখিত! শুধু .txt বা .xlsx ফাইল পাঠান।")

@app.on_message(filters.command("done"))
async def ask_contact_name(client, message):
    await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি **নাম** দিন (যেমন: Yesss):", reply_markup=ForceReply(True))

@app.on_message(filters.reply & filters.text)
async def process_conversion(client, message):
    uid = message.from_user.id
    if uid not in user_data: return

    if 'ctc_name' not in user_data[uid]:
        user_data[uid]['ctc_name'] = message.text
        await message.reply_text("💾 এবার ফাইলের জন্য একটি নাম দিন (যেমন: Injay):", reply_markup=ForceReply(True))
        return
    
    if 'file_name' not in user_data[uid]:
        user_data[uid]['file_name'] = message.text
        await message.reply_text("🔢 প্রতি ফাইলে কতগুলো কন্টাক্ট থাকবে? (যেমন: 200 অথবা সবগুলোর জন্য 'all'):", reply_markup=ForceReply(True))
        return

    limit_text = message.text
    ctc_name = user_data[uid]['ctc_name']
    file_prefix = user_data[uid]['file_name']
    input_file = user_data[uid]['file_path']

    await message.reply_text("⏳ ফাইল প্রসেসিং হচ্ছে... দয়া করে অপেক্ষা করুন।")

    contacts = []
    if input_file.endswith('.txt'):
        with open(input_file, 'r', encoding='utf-8') as f:
            contacts = [line.strip() for line in f if line.strip()]
    else:
        df = pd.read_excel(input_file)
        contacts = df.iloc[:, 0].astype(str).tolist()

    try:
        limit = len(contacts) if limit_text.lower() == 'all' else int(limit_text)
    except:
        limit = len(contacts)
    
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
            
            await message.reply_document(vcf_name)
            os.remove(vcf_name)
            
            vcf_buffer = ""
            count = 0
            file_num += 1

    os.remove(input_file)
    del user_data[uid]
    await message.reply_text("✅ কনভারশন সম্পন্ন হয়েছে!")

# --- পাইথন ৩.১৪ এর জন্য গ্যারান্টিড আধুনিক সমাধান ---
async def start_bot():
    async with app:
        print("Bot is successfully running...")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    try:
        # asyncio.run() নিজে থেকেই নতুন লুপ তৈরি করে নেবে
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error occurred: {e}")
