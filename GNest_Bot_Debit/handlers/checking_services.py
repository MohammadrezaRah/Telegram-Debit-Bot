import os
import pandas as pd
import jdatetime
import asyncio
import re

from aiogram import Router, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



router = Router()



async def check_service_dates(bot: Bot):

    base_path = "./Data_csv/"

    if not os.path.exists(base_path):
        return

    today = jdatetime.date.today()

    user_folders = [
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f))
    ]

    for user_folder in user_folders:

        csv_file_path = os.path.join(
            base_path, user_folder, "installment_purchases.csv"
        )

        if not os.path.exists(csv_file_path):
            continue

        try:
            df = pd.read_csv(
                csv_file_path,
                encoding="utf-8",
                dtype={"order_id": str}
            )
        except Exception as e:
            print(f"❌ خطا در خواندن فایل {csv_file_path}: {e}")
            continue

        if "installment_dates" not in df.columns:
            continue

        try:
            user_id = int(user_folder)
        except ValueError:
            continue

        for index, row in df.iterrows():

            installment_dates = row.get("installment_dates", "")

            if pd.isna(installment_dates):
                continue

            order_id = row.get("order_id", "")
            product_title = row.get("product_title", "محصول خریداری‌شده")

            installment_list = str(installment_dates).splitlines()
            updated_installments = []

            for installment in installment_list:

                match = re.search(
                    r"قسط\s*(\d+)\s*:\s*(\d{4}/\d{1,2}/\d{1,2})\s*:\s*(.*)",
                    installment
                )

                if len(updated_installments) > 0 and "پرداخت نشده" in updated_installments[-1]:
                    break


                if not match:
                    updated_installments.append(installment)
                    continue

                debt_number = match.group(1)
                debt_date = match.group(2)
                debt_status = match.group(3).strip()

                try:
                    year, month, day = map(int, debt_date.split("/"))
                    due_date = jdatetime.date(year, month, day)
                except ValueError:
                    print(f"⚠️ تاریخ نامعتبر در سفارش {order_id}: {debt_date}")
                    updated_installments.append(installment)
                    continue

                days_left = (due_date - today).days

                # اقساط پرداخت‌شده نیازی به بررسی ندارند
                if "پرداخت شده" in debt_status:
                    updated_installments.append(installment)
                    continue

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="پرداخت قسط", callback_data=f"debts_{order_id}")]
                ])

                try:
                    alert_text = None
                    if 0 < days_left <= 3:
                        alert_text = (
                            f"⏰ یادآوری پرداخت قسط\n\n"
                            f"🎮 محصول: {product_title}\n"
                            f"🔢 شماره سفارش: {order_id}\n"
                            f"💳 شماره قسط: {debt_number}\n"
                            f"📅 تاریخ سررسید: {debt_date}\n\n"
                            f"⚠️ {days_left} روز تا سررسید قسط باقی مانده است."
                        )

                    elif days_left == 0:
                        alert_text = (
                            f"🔔 امروز موعد پرداخت قسط است!\n\n"
                            f"🎮 محصول: {product_title}\n"
                            f"🔢 شماره سفارش: {order_id}\n"
                            f"💳 شماره قسط: {debt_number}\n"
                            f"📅 تاریخ سررسید: {debt_date}\n\n"
                            f"لطفاً پرداخت قسط را امروز انجام دهید."
                        )

                    elif 0 > days_left >= -3:
                        alert_text = (
                            f"⚠️🔔 {abs(days_left)} روز از موعد پرداخت قسط گذشته است!\n\n"
                            f"🎮 محصول: {product_title}\n"
                            f"🔢 شماره سفارش: {order_id}\n"
                            f"💳 شماره قسط: {debt_number}\n"
                            f"📅 تاریخ سررسید: {debt_date}\n\n"
                            f"⚠️ لطفاً پرداخت قسط را همین حالا انجام دهید."
                        )

                    elif -3 > days_left > -10:
                        alert_text = (
                            f"⚠️🔔 {abs(days_left)} روز از موعد پرداخت قسط گذشته است!\n\n"
                            f"🎮 محصول: {product_title}\n"
                            f"🔢 شماره سفارش: {order_id}\n"
                            f"💳 شماره قسط: {debt_number}\n"
                            f"📅 تاریخ سررسید: {debt_date}\n\n"
                            f"برای جلوگیری از جریمه ی بیشتر قسط خود را همین حالا پرداخت کنید."
                        )

                    elif days_left == -10:
                        alert_text = (
                            f"⛔📢 {abs(days_left)} روز از موعد پرداخت قسط گذشته است!\n\n"
                            f"🎮 محصول: {product_title}\n"
                            f"🔢 شماره سفارش: {order_id}\n"
                            f"💳 شماره قسط: {debt_number}\n"
                            f"📅 تاریخ سررسید: {debt_date}\n\n"
                            f"❌ برای جلوگیری از باطل شدن اکانت قسط خود را همین حالا پرداخت کنید."
                        )

                    elif days_left == -11:
                        alert_text = (
                            f"📢❌ اکانت شما باطل شد!\n"
                            f"❌ محصول: {product_title}\n"
                            f"❌ شماره سفارش: {order_id}\n"
                        )

                    if alert_text:
                        await bot.send_message(
                            chat_id=user_id,
                            text=alert_text,
                            reply_markup=keyboard
                        )

                except Exception as e:
                    print(
                        f"❌ خطا در ارسال پیام به کاربر {user_id}: {e}"
                    )

                updated_installments.append(installment)

                # حذف فقط قسط پرداخت‌نشده‌ای که ۱۱ روز از موعدش گذشته
                if days_left == -11:
                    await bot.send_message(
                        chat_id=1574768588,
                        text=(
                            f"⚠️❌ {abs(days_left)} روز از موعد پرداخت قسط کاربر گذشته است!\n\n"
                            f"🎮 محصول: {product_title}\n"
                            f"🔢 شماره سفارش: {order_id}\n"
                            f"💳 شماره قسط: {debt_number}\n"
                            f"📅 تاریخ سررسید: {debt_date}\n\n"
                            "\n\n"
                            "کاربر:\n"
                            f"<a href='tg://user?id={user_id}'>{user_id}</a>"

                        ),
                        parse_mode="HTML"
                    )
                    continue

        try:
            df.to_csv(csv_file_path, index=False, encoding="utf-8")
        except Exception as e:
            print(f"❌ خطا در ذخیره فایل {csv_file_path}: {e}")


# تابع برای اجرای بررسی به صورت خودکار هر 24 ساعت
async def schedule_service_check(bot):
    while True:
        # اجرای چک کردن تاریخ سرویس‌ها
        await check_service_dates(bot)
        # منتظر ماندن به مدت 24 ساعت (86400 ثانیه)
        await asyncio.sleep(86520)  # 86400 ثانیه یعنی یک روز


# تابع اصلی برای شروع برنامه
async def on_start(bot):
    print("checking debts...")
    # راه‌اندازی تسک زمان‌بندی شده برای بررسی هر 24 ساعت
    asyncio.create_task(schedule_service_check(bot))


