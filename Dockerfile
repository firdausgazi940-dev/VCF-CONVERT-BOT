# আমরা এখানে পাইথন ৩.১০ ব্যবহার করছি যা একদম স্ট্যাবল
FROM python:3.10-slim

# ফোল্ডার সেটআপ
WORKDIR /app

# ফাইলগুলো কপি করা
COPY . .

# লাইব্রেরি ইন্সটল করা
RUN pip install --no-cache-dir -r requirements.txt

# বোট চালু করা
CMD ["python", "bot.py"]
