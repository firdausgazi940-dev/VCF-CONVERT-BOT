import os, asyncio, threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup

# --- 1. Flask Server (বোটকে অলটাইম সচল রাখতে) ---
server = Flask(__name__)
@server.route('/')
def ping(): return "Super Fast Bot is Running!", 200

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

# --- 2. Bot Credentials ---
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

# sleep_threshold বাড়ানো হয়েছে যাতে টেলিগ্রামের ছোটখাটো ব্লক বোট নিজেই হ্যান্ডেল করে
app = Client("vcf_speed_worker", api_id=api_id, api_hash=api_hash, bot_token=bot_token, sleep_threshold=120)

# --- 3. Commands ---
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"🚀 **VCF Super-Fast Worker**\n\n"
        "**দ্রুত কাজ করার নিয়ম:**\n"
        "১. একটি `.txt` ফাইল পাঠান।\n"
        "২. ফাইলটির রিপ্লাইয়ে নিচের ফরম্যাটে তথ্য দিন:\n"
        "`নাম, ফাইল-কোড, কন্টাক্ট-সংখ্যা, ফাইল-সংখ্যা, শুরুর-নম্বর`\n\n"
        "**উদাহরণ:** `RAKIB, DW, 37, 10, 71`"
    )

@app.on_message(filters.document)
async def handle_document(client, message):
    if message.document.file_name.endswith(".txt"):
        await message.reply_text(f"✅ ফাইল পাওয়া গেছে: `{message.document.file_name}`\nএখন রিপ্লাই দিন।")
    else:
        await message.reply_text("❌ শুধু .txt ফাইল পাঠান।")

# --- 4. High-Speed Processing ---
@app.on_message(filters.reply & filters.text)
async def process_vcf(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return

    try:
        # ইনপুট ডাটা স্প্লিট করা
        input_data = [i.strip() for i in message.text.split(',')]
        if len(input_data) < 5:
            await message.reply_text("❌ ফরম্যাট ভুল! সঠিক উদাহরণ: `RAKIB, DW, 37, 10, 71`")
            return

        c_name, f_prefix, c_per_file, total_files, start_no = input_data
        c_per_file, total_files, start_no = int(c_per_file), int(total_files), int(start_no)

        file_path = await message.reply_to_message.download()
        
        # দ্রুত ফাইল রিডিং
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        # সিকোয়েন্স প্রদর্শন
        sequence_msg = "**Creating Files:**\n"
        for n in range(start_no, start_no + total_files):
            sequence_msg += f"🔹 {f_prefix}{n}.vcf\n"
        status_msg = await message.reply_text(sequence_msg)

        # সুপার ফাস্ট ফাইল জেনারেশন লুপ
        for i in range(total_files):
            current_start = i * c_per_file
            chunk = lines[current_start : current_start + c_per_file]
            if not chunk: break

            file_no = start_no + i
            vcf_fn = f"{f_prefix}{file_no}.vcf"
            
            # মেমোরি অপ্টিমাইজড রাইটিং
            vcard_data = []
            for idx, num in enumerate(chunk):
                vcard_data.append(f"BEGIN:VCARD\nVERSION:3.0\nFN:{c_name} {current_start + idx + 1}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n")
            
            with open(vcf_fn, "w", encoding="utf-8") as vcf:
                vcf.write("".join(vcard_data))
            
            await message.reply_document(vcf_fn)
            os.remove(vcf_fn)
            
            # মিনিমাম সেফটি ডিলে (০.৫ সেকেন্ড)
            await asyncio.sleep(0.5) 

        os.remove(file_path)
        await status_msg.edit("✨ **সবগুলো ফাইল সফলভাবে পাঠানো হয়েছে!**")

    except Exception as e:
        await message.reply_text(f"❌ ভুল হয়েছে: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    app.run()
