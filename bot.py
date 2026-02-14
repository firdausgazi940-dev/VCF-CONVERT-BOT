import os
import asyncio
import pandas as pd
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

# ক্রেডেনশিয়াল সেটআপ (Environment Variable থেকে নেওয়া নিরাপদ)
API_ID = 39509829
API_HASH = "e11187f10974a3416ddf2fc52101a7d9"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# সাময়িকভাবে ডেটা রাখার জন্য ডিকশনারি
user_data = {}

# মেইন মেনু কিবোর্ড (আরও সুন্দরভাবে সাজানো)
main_menu = ReplyKeyboardMarkup(
    [
        ["/to_vcf", "/to_txt", "/manual"],
        ["/add", "/delete", "/renamefile"],
        ["/split", "/count", "/nodup"],
        ["/status", "/vip", "/help"]
    ],
    resize_keyboard=True
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"👋 স্বাগতম **{message.from_user.first_name}**!\n\n"
        "এটি একটি উন্নত VCF কনভার্টার বোট।\n"
        "আপনার কন্টাক্ট ফাইল কনভার্ট করতে **/to_vcf** ক্লিক করুন।",
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
        await message.reply_text(
            "✅ ফাইল সফলভাবে পাওয়া গেছে!\nএখন কনভার্ট শুরু করতে **/done** কমান্ডটি দিন।"
        )
    else:
        await message.reply_text("❌ দুঃখিত! শুধুমাত্র **.txt** বা **.xlsx** ফাইল সাপোর্ট করে।")

@app.on_message(filters.command("done"))
async def ask_contact_name(client, message):
    uid = message.from_user.id
    if uid not in user_data:
        return await message.reply_text("📁 আগে একটি ফাইল পাঠান!")
    
    await message.reply_text("📝 কন্টাক্ট সেভ করার জন্য একটি **নাম** দিন (যেমন: MyContacts):", 
                             reply_markup=ForceReply(True))

@app.on_message(filters.reply & filters.text)
async def process_inputs(client, message):
    uid = message.from_user.id
    if uid not in user_data: return

    # কন্টাক্ট নাম নেওয়া
    if 'ctc_name' not in user_data[uid]:
        user_data[uid]['ctc_name'] = message.text
        await message.reply_text("💾 এবার ফাইলের জন্য একটি নাম দিন (যেমন: Result):", 
                                 reply_markup=ForceReply(True))
        return
    
    # ফাইলের নাম নেওয়া
    if 'file_name' not in user_data[uid]:
        user_data[uid]['file_name'] = message.text
        await message.reply_text("🔢 প্রতি ফাইলে কতগুলো কন্টাক্ট থাকবে?\n(সবগুলোর জন্য **all** লিখুন অথবা সংখ্যা দিন):", 
                                 reply_markup=ForceReply(True))
        return

    # কনভারশন শুরু
    limit_text = message.text
    ctc_name = user_data[uid]['ctc_name']
    file_prefix = user_data[uid]['file_name']
    input_file = user_data[uid]['file_path']

    processing_msg = await message.reply_text("⏳ আপনার ফাইলটি প্রসেসিং হচ্ছে... দয়া করে অপেক্ষা করুন।")

    contacts = []
    try:
        if input_file.endswith('.txt'):
            with open(input_file, 'r', encoding='utf-8') as f:
                contacts = [line.strip() for line in f if line.strip()]
        else:
            df = pd.read_excel(input_file)
            contacts = df.iloc[:, 0].astype(str).tolist()

        if not contacts:
            raise ValueError("ফাইলটি খালি!")

        limit = len(contacts) if limit_text.lower() == 'all' else int(limit_text)
    except Exception as e:
        return await message.reply_text(f"❌ এরর: {str(e)}")
    
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
            
            vcf_buffer = ""
            count = 0
            file_num += 1

    await processing_msg.delete()
    await message.reply_text("✨ অভিনন্দন! আপনার সব ফাইল সফলভাবে তৈরি করা হয়েছে।", reply_markup=main_menu)
    
    # ক্লিনআপ
    if os.path.exists(input_file): os.remove(input_file)
    user_data.pop(uid, None)

# --- পাইথন ৩.১৪ রানটাইম হ্যান্ডলিং ---
async def run_bot():
    async with app:
        print("✅ Bot is Live and Running on Render!")
        from pyrogram.methods.utilities.idle import idle
        await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        pass
