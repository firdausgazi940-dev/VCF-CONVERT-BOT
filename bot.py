import os, asyncio, threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

# --- 1. Flask Server ---
server = Flask(__name__)
@server.route('/')
def ping(): return "Bot is Running!", 200

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

# --- 2. Bot Credentials ---
api_id = 39509829
api_hash = "e11187f10974a3416ddf2fc52101a7d9"
bot_token = os.environ.get("BOT_TOKEN", "8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss")

app = Client("vcf_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token, sleep_threshold=120)

user_data = {}

# Main Menu Keyboard
main_menu = ReplyKeyboardMarkup(
    [["/to_vcf", "/admin", "/help"]],
    resize_keyboard=True
)

# --- 3. Commands ---
@app.on_message(filters.command("start"))
async def start(client, message):
    # আপনার দেওয়া ফটো লিঙ্কটি এখানে অ্যাড করা হয়েছে
    photo_url = "https://photos.app.goo.gl/J2B5nGFdDRbCCtGL9"
    await message.reply_photo(
        photo=photo_url,
        caption=f"🚀 **AMG ABDUL VCF WORKER**\n\n"
                f"Hello **{message.from_user.first_name}**!\n"
                f"একটি .txt ফাইল পাঠান এবং ৫৩৮১ স্টাইলে রিপ্লাই দিন।\n\n"
                f"**Format:** `Name, FileCode, Contacts, Files, StartNo`",
        reply_markup=main_menu
    )

@app.on_message(filters.document)
async def handle_document(client, message):
    if message.document.file_name.endswith(".txt"):
        await message.reply_text(
            "✅ File Received!\n\n"
            "এখন নিচের ফরম্যাটে রিপ্লাই দিন:\n"
            "`RAKIB, DW, 37, 10, 71`"
        )
    else:
        await message.reply_text("❌ Please send a .txt file.")

# --- 4. High-Speed Advanced Handler ---
@app.on_message(filters.reply & filters.text)
async def handle_advanced_vcf(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return

    try:
        # ৫৩৮১ স্টাইলে ইনপুট প্রসেসিং
        input_data = [i.strip() for i in message.text.split(',')]
        if len(input_data) < 5:
            await message.reply_text("❌ ফরম্যাট ভুল! উদাহরণ: `RAKIB, DW, 37, 10, 71`")
            return

        c_name, f_prefix, c_limit, f_count, s_no = input_data
        c_limit, f_count, s_no = int(c_limit), int(f_count), int(s_no)

        file_path = await message.reply_to_message.download()
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        # সিকোয়েন্স দেখানো
        seq_msg = "**File name sequence to be created:**\n"
        for n in range(s_no, s_no + f_count):
            seq_msg += f"{f_prefix} {n}\n"
        await message.reply_text(seq_msg)

        # সুপার ফাস্ট জেনারেশন (০.২ সেকেন্ড ডিলে)
        for i in range(f_count):
            start_idx = i * c_limit
            chunk = lines[start_idx : start_idx + c_limit]
            if not chunk: break

            current_no = s_no + i
            vcf_fn = f"{f_prefix}{current_no}.vcf"
            
            with open(vcf_fn, "w", encoding="utf-8") as vcf:
                for idx, num in enumerate(chunk):
                    vcf.write(f"BEGIN:VCARD\nVERSION:3.0\nFN:{c_name} {start_idx + idx + 1}\nTEL;TYPE=CELL:{num}\nEND:VCARD\n")
            
            await message.reply_document(vcf_fn)
            os.remove(vcf_fn)
            # আপনার রিকোয়েস্ট অনুযায়ী ০.২ সেকেন্ড বিরতি
            await asyncio.sleep(0.2) 

        os.remove(file_path)
        await message.reply_text("✨ Conversion complete!")

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    app.run()
