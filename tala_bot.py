import sqlite3
import requests
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

# توکن ربات و شناسه کانال تلگرام
TELEGRAM_BOT_TOKEN = "7904421118:AAEA00YE0AOcKQ4hpHpy8hsvTx0oeSRazxs"
TELEGRAM_CHANNEL_ID = "@irantt_gold"

# مسیر دیتابیس
DB_PATH = "gold_price.db"

# تابع برای ایجاد جدول در دیتابیس
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_price (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price REAL,
            time TEXT,
            change_percent REAL,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()

# تابع برای دریافت قیمت قبلی از دیتابیس
def get_previous_price():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM gold_price ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# تابع برای ذخیره قیمت جدید در دیتابیس
def save_new_price(price, time, change_percent):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO gold_price (price, time, change_percent, last_updated)
        VALUES (?, ?, ?, ?)
    """, (price, time, change_percent, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# تابع برای دریافت قیمت طلای 18 عیار از API
def fetch_gold_price():
    url = "https://brsapi.ir/FreeTsetmcBourseApi/Api_Free_Gold_Currency_v2.json"
    response = requests.get(url)
    
    try:
        data = response.json()
        print("API Response:", data)
    except ValueError:
        print("خطا در تبدیل پاسخ API به فرمت JSON")
        return None, None, None
    
    for item in data.get("gold", []):
        if item["name"] == "طلای 18 عیار":
            gold_price = item.get("price", "نامشخص")
            gold_time = item.get("time", "نامشخص")
            gold_change = item.get("change_percent", "نامشخص")
            return gold_price, gold_time, gold_change
    
    return None, None, None

# تابع برای ارسال پیام به تلگرام با دکمه لینک
async def send_to_telegram():
    # دریافت قیمت طلا
    price, time, change = fetch_gold_price()
    if price is None or time is None:
        return

    try:
        price = float(price)
    except ValueError:
        price = 0

    # دریافت قیمت قبلی
    previous_price = get_previous_price()

    # اگر قیمت تغییر کرده باشد، پیام ارسال کن
    if previous_price is None or price != previous_price:
        save_new_price(price, time, change)
        message = f"""
        ایران تی تی | iran TT

        🔔 طلای 18 عیار:
        💰 قیمت: {price:,.0f} تومان
        -----------------------------------

        📅 زمان: {time}
        📈 تغییرات: {change}%
        
        ایران تی تی - خرید و فروش طلا آنلاین
        """

        keyboard = [[InlineKeyboardButton("مشاهده سایت", url="https://irantt.com")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, reply_markup=reply_markup)
            print("پیام ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال پیام: {e}")

# تابع برای اجرای برنامه
async def main():
    while True:
        await send_to_telegram()
        await asyncio.sleep(60)

# اجرای برنامه
if __name__ == "__main__":
    initialize_database()  # ایجاد دیتابیس و جدول در صورت نیاز
    print("ربات شروع به کار کرد...")
    asyncio.run(main())
