import telebot

# আপনার দেওয়া আসল টোকেন সরাসরি এখানে বসানো হয়েছে
API_TOKEN = '8338204876:AAG8Y3F30W115DyG3HkwvTRGkbHayGh43Ss'

# বোট অবজেক্ট তৈরি
bot = telebot.TeleBot(API_TOKEN)

# /start এবং /help কমান্ডের রিপ্লাই
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "অভিনন্দন! আপনার VCF কনভার্টার বোটটি এখন সক্রিয় আছে।\n\nআমাকে আপনার ফাইল পাঠান অথবা মেসেজ দিন।")

# যেকোনো টেক্সট মেসেজের রিপ্লাই
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "আমি আপনার মেসেজটি পেয়েছি। আপনার সেবার জন্য আমি প্রস্তুত!")

# বোটটি চালু করা
print("Bot is successfully running...")
bot.infinity_polling()

