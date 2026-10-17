from aiogram import types, Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import pandas as pd

router = Router()


class Change(StatesGroup):
    waiting_for_name_user_info = State()
    waiting_for_user_id = State()  # ذخیره آیدی کاربر


@router.message(F.text == "مشاهده اطلاعات کاربر")
async def request_username(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )
    await message.answer("یوزرنیم یا آیدی عددی کاربر را وارد کنید:", reply_markup=keyboard)
    await state.set_state(Change.waiting_for_name_user_info)


@router.message(Change.waiting_for_name_user_info)
async def search_and_show_user_info(message: Message, state: FSMContext):
    username = message.text.strip()
    username = username.lstrip('@') if "@" in username else username

    user_found = False
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="دیدن سرویس های کاربر", callback_data="show_user_services")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )

    # جستجو در دایرکتوری کاربر
    for user_dir in os.listdir("Data_csv"):
        user_path = os.path.join("Data_csv", user_dir, f"{user_dir}.csv")

        if os.path.exists(user_path):
            df = pd.read_csv(user_path, encoding="utf-8")
            if "id" not in df.columns or "username" not in df.columns:
                await message.answer("❌ فایل داده‌ها ناقص است.")
                return

            if username.isdigit():
                df["id"] = df["id"].astype(str)
                user_row = df[df["id"] == username]
            else:
                user_row = df[df["username"] == username]

            if not user_row.empty:
                user_found = True
                user_info = user_row.iloc[0]
                info_text = (
                    f"👤 یوزرنیم: {user_info['username']}\n"
                    f"🆔 آیدی: <code>{user_info['id']}</code>\n"
                    f"📜 قوانین پذیرفته شده: {'بله' if user_info['law'] else 'خیر'}\n"
                    f"💰 موجودی کیف پول: {int(user_info['wallet']):,} تومان\n"
                    f"🧪 تست V2Ray: {'دریافت کرده' if user_info['test_v2ray'] else 'دریافت نکرده'}\n"
                    f"🧪 تست OpenVPN: {'دریافت کرده' if user_info['test_ovpn'] else 'دریافت نکرده'}\n"
                    f"🛍️ سرویس‌های خریداری شده: {user_info['services']} عدد "
                )
                await message.answer(info_text, parse_mode="HTML", reply_markup=keyboard)

                # ذخیره user_id در context
                user_id = user_info["id"]
                await state.update_data(user_id=user_id)
                break

    if not user_found:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
            ]
        )
        await message.answer("❌ یوزرنیم یا آیدی مورد نظر یافت نشد. لطفاً دوباره تلاش کنید:", reply_markup=keyboard)


@router.callback_query(F.data == "show_user_services")
async def show_user_services(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")  # دریافت user_id از context

    if not user_id:
        await callback.message.edit_text("❌ اطلاعات کاربر یافت نشد.")
        return

    csv_file = f"Data_csv/{user_id}/user_service_data.csv"

    if not os.path.exists(csv_file):
        await callback.message.edit_text("❌ هیچ سرویسی برای این کاربر یافت نشد.")
        return

    # خواندن داده‌ها از فایل CSV
    df = pd.read_csv(csv_file, encoding="utf-8")
    if df.empty:
        await callback.message.edit_text("❌ هیچ سرویسی برای این کاربر یافت نشد.")
        return

    # ساخت دکمه‌ها برای نمایش سرویس‌ها
    inline_buttons = []
    for index, row in df.iterrows():
        service_name = row['service_name']
        button_text = f"🔒 {service_name}"
        button = InlineKeyboardButton(text=button_text, callback_data=f"user_service_{index}")
        inline_buttons.append([button])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_buttons + [[InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]]
    )
    await callback.message.edit_text("لیست سرویس‌های فعال برای شما:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("user_service_"))
async def show_service_details(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")  # دریافت user_id از context
    index = int(callback.data.split("_")[2])
    csv_file = f"Data_csv/{user_id}/user_service_data.csv"

    if not os.path.exists(csv_file):
        await callback.message.edit_text("❌ فایل سرویس‌ها یافت نشد.")
        return

    # خواندن داده‌ها از فایل CSV
    df = pd.read_csv(csv_file, encoding="utf-8")
    if index >= len(df):
        await callback.message.edit_text("❌ سرویس مورد نظر یافت نشد.")
        return

    service = df.iloc[index]
    text = (
        f"🔒 <b>{service['service_name']}</b>\n"
        f"👤 یوزرنیم: <code>{service['username']}</code>\n"
        f"🔑 رمز: <code>{service['password']}</code>\n"
        f"⏳ مدت: {service['length']} \n"
        f"📆 شروع سرویس: {service['start_date']}\n"
        f"📆 پایان سرویس: {service['end_date']}\n"
        f"🧬 سرویس: {service['services']}\n"
        f"💳 مبلغ سرویس: {int(service['amount']):,} تومان\n"
        f"🔗 لینک اتصال: {service['line']}"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 حذف سرویس کاربر", callback_data=f"confirm_user_delete_{index}")],
            [InlineKeyboardButton(text="🔙 بازگشت به لیست سرویس ها", callback_data="show_user_services")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith('confirm_user_delete_'))
async def confirm_delete_service(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")  # دریافت user_id از context
    index = int(callback_query.data.split("_")[3])
    csv_file = f"Data_csv/{user_id}/user_service_data.csv"

    if not os.path.exists(csv_file):
        await callback.message.edit_text("❌ فایل سرویس‌ها یافت نشد.")
        return

    # خواندن داده‌ها از فایل CSV
    df = pd.read_csv(csv_file, encoding="utf-8")
    if index >= len(df):
        await callback.message.edit_text("❌ سرویس مورد نظر یافت نشد.")
        return

    service = df.loc[index, "service_name"]
    service_name = service
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ بله، حذف کن", callback_data=f"user_delete_{service_name}")],
            [InlineKeyboardButton(text="🔙 خیر", callback_data=f"user_service_{index}")],
        ]
    )
    await callback_query.message.edit_text(
        f"⚠️ آیا از حذف سرویس '{service_name}' اطمینان دارید؟",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('user_delete_'))
async def delete_service(callback_query: types.CallbackQuery, state: FSMContext):
    service_name = callback_query.data[len('user_delete_'):]
    data = await state.get_data()
    user_id = data.get("user_id")  # دریافت user_id از context
    csv_file = os.path.join(f"Data_csv/{user_id}", "user_service_data.csv")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به لیست سرویس‌ها", callback_data=f"show_user_services")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding="utf-8")
        df = df[df['service_name'] != service_name]
        df.to_csv(csv_file, index=False, encoding="utf-8")
        await callback_query.message.edit_text(f"✅ سرویس '{service_name}' با موفقیت حذف شد.", reply_markup=keyboard)
    else:
        await callback_query.message.answer("❌ فایل سرویس‌ها یافت نشد.")

    await callback_query.answer()
