import csv
import re
import os
import pandas as pd
import jdatetime
from aiogram import Router, types, F
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


router = Router()


class AddLinkState(StatesGroup):
    choosing_path = State()
    choosing_column = State()
    getting_text = State()
    getting_start_line = State()
    getting_text_final = State()


@router.message(F.text == "اضافه کردن لینک")
async def choose_path(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛰️ OpenVPN", callback_data="openvpn_dir")],
            [InlineKeyboardButton(text="دیدن فایل خرید ها", callback_data="see_buy_file")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
    )
    await message.answer("⚠️ یک گزینه انتخاب کنید.", reply_markup=keyboard)


@router.callback_query(F.data == "file_lists")
async def choose_path(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛰️ OpenVPN", callback_data="openvpn_dir")],
            [InlineKeyboardButton(text="دیدن فایل خرید ها", callback_data="see_buy_file")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
    )
    await callback_query.message.edit_text("⚠️ یک گزینه انتخاب کنید.", reply_markup=keyboard)


@router.callback_query(F.data == 'see_buy_file')
async def handle_buy(callback_query: types.CallbackQuery):

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="این ماه", callback_data="this_month_buy_file")],
            [InlineKeyboardButton(text="ماه قبل", callback_data="last_month_buy_file")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="file_lists")]
        ]
    )
    await callback_query.message.edit_text("برای دیدن فایل گزینه زیر را لمس کنید:", reply_markup=inline_keyboard)
    await callback_query.answer()


@router.callback_query(F.data == 'this_month_buy_file')
async def handle_buy_this_month(callback_query: types.CallbackQuery, state: FSMContext):
    buy_folder = "./Buy_Counting"
    os.makedirs(buy_folder, exist_ok=True)  # ایجاد پوشه در صورت نبودن
    this_month_buy_file = jdatetime.date.today().strftime("%Y-%m")
    csv_buy = f"{buy_folder}/Count_{this_month_buy_file}"
    await state.update_data(path=csv_buy)

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ارسال فایل", callback_data="sending_csv")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="file_lists")]
        ]
    )
    await callback_query.message.edit_text("برای دیدن فایل گزینه زیر را لمس کنید:", reply_markup=inline_keyboard)
    await callback_query.answer()


@router.callback_query(F.data == 'last_month_buy_file')
async def handle_buy_last_month(callback_query: types.CallbackQuery, state: FSMContext):
    buy_folder = "./Buy_Counting"
    os.makedirs(buy_folder, exist_ok=True)  # ایجاد پوشه در صورت نبودن
    today = jdatetime.date.today()
    last_month = today.replace(day=1) - jdatetime.timedelta(days=1)
    last_month_buy_file = last_month.strftime("%Y-%m")
    csv_buy = f"{buy_folder}/Count_{last_month_buy_file}"
    await state.update_data(path=csv_buy)

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ارسال فایل", callback_data="sending_csv")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="file_lists")]
        ]
    )
    await callback_query.message.edit_text("برای دیدن فایل گزینه زیر را لمس کنید:", reply_markup=inline_keyboard)
    await callback_query.answer()


@router.callback_query(F.data == 'openvpn_dir')
async def handle_test_v2ray(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="./Services/openvpn/test_openvpn.csv")],
            [KeyboardButton(text="./Services/openvpn/openvpn_1month_unlimited.csv")],
            [KeyboardButton(text="./Services/openvpn/openvpn_2month_unlimited.csv")],
            [KeyboardButton(text="./Services/openvpn/openvpn_3month_unlimited.csv")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )
    await callback_query.message.answer("لطفاً مسیر ذخیره‌سازی را انتخاب کنید:", reply_markup=keyboard)
    await state.set_state(AddLinkState.choosing_path)
    await callback_query.answer()



@router.message(AddLinkState.choosing_path)
async def choose_column(message: types.Message, state: FSMContext):
    await state.update_data(path=message.text)
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ارسال فایل", callback_data="sending_csv")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="file_lists")]
        ]
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="link")],
            [KeyboardButton(text="username")],
            [KeyboardButton(text="password")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )
    await message.answer("در کدام ستون می‌خواهید اضافه کنید؟", reply_markup=keyboard)
    await message.answer("یا میخوای فایل رو ببینی؟", reply_markup=inline_keyboard)
    await state.set_state(AddLinkState.choosing_column)


@router.message(AddLinkState.choosing_column)
async def get_text(message: types.Message, state: FSMContext):
    column = message.text
    fieldnames = ["link", "username", "password"]
    if column not in fieldnames:
        await message.answer("نام ستون نامعتبر است.")
        return
    await state.update_data(column=message.text)
    await message.answer("از کدام خط می‌خواهید اضافه شود؟ عددی ارسال کنید:")
    await state.set_state(AddLinkState.getting_start_line)


@router.message(AddLinkState.getting_start_line)
async def get_start_line(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("لطفاً یک عدد معتبر ارسال کنید.")
        return
    start_line = int(message.text)
    await state.update_data(start_line=start_line)
    await message.answer("حالا متن را ارسال کنید:")
    await state.set_state(AddLinkState.getting_text_final)


@router.message(AddLinkState.getting_text_final)
async def convert_to_csv_final(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ارسال فایل", callback_data="sending_csv")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="file_lists")]
        ]
    )
    data = await state.get_data()
    path = data.get("path")
    column = data.get("column")
    start_line = data.get("start_line", 0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    values = message.text.split("\n")
    try:
        df = pd.read_csv(path, encoding="utf-8") if os.path.exists(path)\
            else pd.DataFrame(columns=["link", "username", "password"])
        for i, value in enumerate(values):
            index = start_line + i
            if index < len(df):
                df.at[index, column] = value
            else:
                new_row = {col: "" for col in df.columns}
                new_row[column] = value
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(path, index=False, encoding="utf-8")
    except Exception as e:
        await message.answer(f"خطایی رخ داد: {e}")
        return
    await message.answer("انجام شد", reply_markup=keyboard)
    await state.set_state(AddLinkState.choosing_column)


@router.callback_query(F.data == 'sending_csv')
async def handle_test_v2ray(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    path = data["path"]
    try:
        df = pd.read_csv(path, encoding="utf-8")
        # نمایش محتویات فایل CSV همراه با ایندکس‌ها به صورت متن
        csv_text = df.to_string(index=True)
        # ارسال محتویات به صورت متن فرمت‌شده
        await callback_query.message.answer(f"محتویات فایل CSV:\n\n{csv_text}")
        # ارسال فایل CSV به صورت فایل
        await callback_query.message.answer_document(FSInputFile(path))
    except Exception as e:
        await callback_query.message.answer(f"خطایی رخ داد: {e}")

    await callback_query.answer()
