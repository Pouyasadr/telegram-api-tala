import requests
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# توکن ربات و شناسه کانال تلگرام
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHANNEL_ID = "@irantt_gold"

# متغیر برای ذخیره قیمت قبلی
previous_price = None

# تابع برای دریافت قیمت طلای 18 عیار از API
def fetch_gold_price():
    url = "https://brsapi.ir/FreeTsetmcBourseApi/Api_Free_Gold_Currency_v2.json"
    response = requests.get(url)
    
    # چاپ پاسخ API برای بررسی
    try:
        data = response.json()
        print("API Response:", data)  # نمایش پاسخ برای بررسی
    except ValueError:
        print("خطا در تبدیل پاسخ API به فرمت JSON")
        return "نامشخص", "نامشخص", "نامشخص"  # در صورت خطا در تبدیل، مقادیر پیش‌فرض می‌دهیم
    
    # جستجو برای طلای 18 عیار در داده‌ها
    for item in data.get("gold", []):
        if item["name"] == "طلای 18 عیار":
            gold_price = item.get("price", "نامشخص")
            gold_time = item.get("time", "نامشخص")
            gold_change = item.get("change_percent", "نامشخص")
            return gold_price, gold_time, gold_change
    
    # اگر طلای 18 عیار یافت نشد، مقادیر پیش‌فرض برمی‌گردانیم
    return "نامشخص", "نامشخص", "نامشخص"

# تابع برای ارسال پیام به تلگرام با دکمه لینک
async def send_to_telegram():
    global previous_price
    
    # دریافت قیمت طلا
    price, time, change = fetch_gold_price()
    
    # اطمینان از اینکه قیمت به عدد صحیح تبدیل شده
    try:
        price = float(price)  # تبدیل به float برای جلوگیری از خطا
    except ValueError:
        price = 0  # در صورت اشتباه بودن داده‌ها، مقدار پیش‌فرض صفر قرار می‌دهیم
    
    # محدود کردن تعداد اعشار و اضافه کردن جداکننده هزارگان
    price = round(price, 0)  # قیمت را به عدد صحیح تبدیل می‌کنیم
    
    # بررسی تغییر قیمت
    if previous_price is None or price != previous_price:
        # ذخیره قیمت جدید
        previous_price = price
        
        # ساخت پیام با دکمه لینک
        message = f"""
        ایران تی تی | iran TT

        🔔 طلای 18 عیار:
        💰 قیمت: {price:,.0f} تومان
        -----------------------------------

        📅 زمان: {time}
        📈 تغییرات: {change}%
        
        ایران تی تی - خرید و فروش طلا آنلاین
        """
        
        # تعریف دکمه inline با لینک به سایت
        keyboard = [
            [InlineKeyboardButton("مشاهده سایت", url="https://irantt.com")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # چاپ پیام پیش از ارسال به تلگرام
        print("متن پیام ارسال‌شده به تلگرام:\n", message)
        
        # ارسال پیام به کانال تلگرام همراه با دکمه
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, reply_markup=reply_markup)
            print("پیام ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال پیام: {e}")

# تابع برای اجرای برنامه‌ریزی و ارسال پیام زمانی که قیمت تغییر کند
async def main():
    while True:
        await send_to_telegram()
        await asyncio.sleep(60)  # هر 60 ثانیه یکبار چک می‌کند

# اجرای برنامه
if __name__ == "__main__":
    print("ربات شروع به کار کرد...")
    asyncio.run(main())  # اجرای برنامه همزمان
