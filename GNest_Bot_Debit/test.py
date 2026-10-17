import os
import re
import pandas as pd
from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers import store


class OVPN(StatesGroup):
    waiting_for_link = State()
    waiting_for_name = State()
    waiting_rejection_reason = State()


router = Router()
SUPPORT_CHAT_ID = -1002514232312



@router.callback_query(F.data == "buy_1month_ovpn_5gb")
async def one_month_unlimited(callback_query: types.CallbackQuery, state: FSMContext):
    length = "1 ماه"
    services = "1 کاربر 5 گیگ openvpn"
    data = await state.get_data()
    amount = data.get("amount_open_5gb_1m")
    amount_formatted = "{:,.0f}".format(amount)  # فرمت کردن مبلغ
    file_path = "./Services/openvpn/openvpn_1month_unlimited.csv"
    # ایجاد کیبورد با دکمه‌های "بازگشت" و "پرداخت"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 پرداخت", callback_data="go_pay")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="unlimited_openvpn")],
        ]
    )

    await callback_query.message.edit_text(
        f"📌هزینه این سرویس {amount_formatted} تومان میباشد. \n",
        reply_markup=keyboard
    )
    # ذخیره مقدار length و services در state
    await state.update_data(length=length, services=services, amount=amount, file_path=file_path)



@router.message(OVPN.waiting_for_name)
async def get_service_name(message: types.Message, state: FSMContext, bot: Bot):

    user_data = await state.get_data()
    amount = user_data.get("amount")
    length = user_data.get("length")  # دریافت مقدار length
    services = user_data.get("services")  # دریافت مقدار services
    service_name = message.text.strip()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ ارسال لینک", callback_data="send_info_ovpn")],
            [InlineKeyboardButton(text="❌ رد درخواست", callback_data="reject_req")]
        ]
    )

    # ساخت متن پیام به صورت کامل
    if message.from_user.username:
        user_info = f"@{message.from_user.username}"
    else:
        user_info = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>"

    text = (
        "🛠️ درخواست خرید سرویس جدید!\n\n"
        f"👤 کاربر: {user_info}\n"
        f"🆔 آیدی عددی: <code>{message.from_user.id}</code>\n"
        f"🔧 نام سرویس: {service_name}\n"
        f"🔢 نوع سرویس: {services}\n"
        f"💰 مبلغ پرداخت شده: {amount}\n"
        f"⏳ مدت سرویس: {length}\n"
    )

    # ارسال پیام
    await bot.send_message(
        SUPPORT_CHAT_ID,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    await message.answer("✅ درخواست خرید شما ثبت شد و در انتظار تایید پشتیبانی می‌باشد!\n"
                         "لطفا منتظر بمانید...")



@router.callback_query(F.data == "send_info_ovpn")
async def accepted(callback_query: types.CallbackQuery, state: FSMContext):

    text = callback_query.message.text

    user_id_match = re.search(r"🆔 آیدی عددی:\s*(\d+)", text)
    username_match = re.search(r"@([\w\d_]+)", text)
    service_name = re.search(r"🔧 نام سرویس: (.+)", text)
    services = re.search(r"🔢 نوع سرویس: (.+)", text)
    amount = re.search(r"💰 مبلغ پرداخت شده: (.+)", text)
    length = re.search(r"⏳ مدت سرویس: (.+)", text)

    user_id = user_id_match.group(1)
    user_username = username_match.group(1) if username_match else "نامشخص"
    service_name = service_name.group(1) if service_name else "نامشخص"
    services = services.group(1) if services else "نامشخص"
    amount = amount.group(1) if amount else "نامشخص"
    length = length.group(1) if length else "نامشخص"

    await callback_query.message.edit_text("لینک سرویس را وارد کنید:")


    await state.set_state(store.Change.waiting_for_unlimited_v2ray_link)
    await state.update_data(user_id=user_id, user_username=user_username, service_name=service_name,
                            length=length, services=services, amount=amount)


@router.callback_query(F.data == "reject_req")
async def rejection(callback_query: types.CallbackQuery, state: FSMContext):
    try:

        text = callback_query.message.text

        user_id_match = re.search(r"🆔 آیدی عددی:\s*(\d+)", text)
        user_name = re.search(r"@([\w\d_]+)", text)
        service_name = re.search(r"🔧 نام سرویس: (.+)", text)
        amount = re.search(r"💰 مبلغ پرداخت شده: (.+)", text)


        user_id = user_id_match.group(1) if user_id_match else "نامشخص"
        user_name = user_name.group(1) if user_name else "نامشخص"
        amount = amount.group(1) if amount else "نامشخص"
        service_name = service_name.group(1) if service_name else "نامشخص"

        csv_file = f"Data_csv/{user_id}/{user_id}.csv"
        if not os.path.exists(csv_file):
            await callback_query.message.answer("⛔ فایل کاربر پیدا نشد.")
            return

        df = pd.read_csv(csv_file, encoding="utf-8")
        wallet_balance = int(df["wallet"].iloc[0])
        new_wallet_balance = wallet_balance + int(amount)
        df["wallet"] = new_wallet_balance
        df.to_csv(csv_file, index=False, encoding="utf-8")

        await callback_query.message.edit_text("لطفا دلیل رد درخواست را بنویسید:")

        await state.set_state(OVPN.waiting_rejection_reason)
        await state.update_data(user_id=user_id, user_name=user_name, service_name=service_name, amount=amount)

    except Exception as e:
        await callback_query.message.answer(f"⛔ خطا در رد درخواست:\n{e}")


@router.message(OVPN.waiting_rejection_reason)
async def process_rejection_reason(message: types.Message, state: FSMContext, bot: Bot):
    # دریافت یادداشت از پشتیبانی
    rejection_reason = message.text.strip()

    # گرفتن داده‌ها از FSM
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    user_name = user_data.get("user_name")
    service_name = user_data.get("service_name")
    amount = user_data.get("amount")
    amount_formatted = "{:,.0f}".format(int(amount))


    # ارسال پیام به پشتیبانی که سرویس رد شد
    await message.answer(
        f"❌ درخواست خرید سرویس رد شد!\n"
        f"رد شده توسط: {message.from_user.id}\n\n"
        f"👤 کاربر:\n @{user_name} (ID: {user_id})\n"
        f"🔧 نام سرویس: {service_name}\n"
        f"📅 دلیل رد درخواست:\n{rejection_reason}\n"
    )

    # ارسال پیام به کاربر مبنی بر رد شدن تمدید همراه با یادداشت
    await bot.send_message(
        user_id,
        f"❌ درخواست خرید سرویس شما رد شد و مبلغ {amount} تومان به کیف پول شما مرجوع گردید.\n\n"
        f"🔧 نام سرویس: {service_name}\n"
        f"📜 دلیل رد تمدید:\n{rejection_reason}"
    )

    # پاک کردن داده‌های FSM
    await state.clear()


