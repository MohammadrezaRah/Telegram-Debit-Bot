from aiogram import types, Router, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import os
import re
import pandas as pd



router = Router()

check_gp = -1003737591897


class Change(StatesGroup):
    waiting_for_amount = State()
    waiting_for_photo = State()
    waiting_rejection_reason = State()



@router.message(F.text == "💳 کیف پول و شارژ")
async def wallet_balance(message: types.Message):
    user_id = message.chat.id
    directory = f"Data_csv/{user_id}"
    file_path = os.path.join(directory, f"{user_id}.csv")

    # بررسی وجود فایل CSV
    if os.path.exists(file_path):
        # خواندن موجودی از فایل CSV
        df = pd.read_csv(file_path)
        wallet_balance = df["wallet"].iloc[0]  # فرض می‌کنیم موجودی در اولین سطر است
        wallet_balance_balance_formatted = "{:,.0f}".format(wallet_balance)
        await message.answer(" ✨ با این موجودی، شما به راحتی می‌توانید از خدمات مختلف ما استفاده کنید."
                             " اگر سوالی دارید یا به کمک نیاز دارید، با پشتیبانی ارتباط بگیرید."
                             "  تیم ما همیشه آماده کمک به شماست!"
                             f"\n\n 💰 موجودی کیف پول شما: {wallet_balance_balance_formatted} تومان\n"
                             f"🆔 آیدی شما: <code>{message.from_user.id}</code>",
                             parse_mode="HTML",
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [InlineKeyboardButton(text="⚡ شارژ کیف پول", callback_data="charge_wallet")],
                                     [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
                                 ]
                             ))
    else:
        await message.answer("❌ فایل اطلاعات کیف پول پیدا نشد. لطفاً از گزینه /start استفاده کنید.")


@router.callback_query(F.data == "charge_wallet")
async def charge_wallet(callback_query: types.CallbackQuery):
    # ایجاد دکمه "💵 وارد کردن مبلغ و بررسی"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 کارت به کارت", callback_data="Card_transfer")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
    )
    await callback_query.message.edit_text("با چه روشی مایل به شارژ هستید؟",
                                           reply_markup=keyboard)


def convert_persian_to_english(text):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translation_table = str.maketrans(persian_digits, english_digits)
    return text.translate(translation_table)


def normalize_amount(amount_str):
    """حذف کاما، `+` و تبدیل اعداد فارسی به انگلیسی"""
    return convert_persian_to_english(amount_str.replace(",", "").replace("+", "").strip())


@router.callback_query(F.data == "Card_transfer")
async def charge_wallet(callback_query: types.CallbackQuery, state: FSMContext):
    # ایجاد دکمه "💵 وارد کردن مبلغ و بررسی"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 وارد کردن مبلغ و بررسی", callback_data="enter_amount")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
    )
    second_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💵 درگاه آنلاین", callback_data="online_pay")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
    )


    # مسیر فایل CSV شماره کارت‌ها
    cards_folder = "./Cards"
    card_file_path = os.path.join(cards_folder, "cards.csv")
    if os.path.exists(card_file_path):
        df = pd.read_csv(card_file_path)

        card_info = df[['card_number', 'name', 'count']]

        # ارسال اطلاعات به کاربر
        for index, row in card_info.iterrows():
            if row["count"] < 190:
                card_number = row['card_number']
                name = row['name']
                await callback_query.message.edit_text(f"💳 شماره کارت: <code>{card_number}</code>\n👤 صاحب حساب: {name}\n\n"
                                                       f"🔍 لطفاً 'بعد' از انجام عملیات گزینه‌ی بررسی را لمس کنید.",
                                                       parse_mode="HTML",
                                                       reply_markup=keyboard
                                                       )
                await state.update_data(card_number=card_number)
                break
            else:
                await callback_query.message.edit_text("ظرفیت کارت به کارت پر شده است،"
                                                       " لطفا از طریق پشتیبانی اقدام کنید.",
                                                       reply_markup=second_keyboard)

    else:
        await callback_query.message.edit_text("❌ فایل اطلاعات کارت‌ها یافت نشد. لطفاً با پشتیبانی تماس بگیرید.")


@router.callback_query(F.data == "enter_amount")
async def enter_amount(callback_query: types.CallbackQuery, state: FSMContext):
    # ارسال پیام برای دریافت مبلغ انتقال
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
        ]
    )
    await callback_query.message.edit_text("💵 لطفاً مبلغ انتقال داده‌شده را وارد کنید (به ریال)", reply_markup=keyboard)
    await state.set_state(Change.waiting_for_amount)  # وضعیت برای دریافت مبلغ


@router.message(Change.waiting_for_amount)
async def get_amount(message: types.Message, state: FSMContext):
    try:
        # تبدیل ورودی به عدد
        amount = int(message.text.strip())
        if amount < 10000:
            await message.answer("⛔ مبلغ وارد شده کمتر از حد مجاز است.(۱۰,۰۰۰ ریال)"
                                 "\nلطفاً دوباره بررسی کنید و "
                                 "مبلغ را به ریال وارد کنید."
                                 )
            await state.set_state(Change.waiting_for_amount)  # وضعیت برای دریافت مبلغ
            return

        if amount <= 0:
            await message.answer("⛔ عدد وارد شده صحیح نیست. لطفاً عددی بزرگتر از صفر وارد کنید.")
            await state.set_state(Change.waiting_for_amount)
            return

        else:
            await state.update_data(amount=amount)  # ذخیره مبلغ در وضعیت
            # ارسال پیام برای دریافت ساعت رسید انتقال
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")
                ]]
            )
            await message.answer("⏰ لطفاً تصویر رسید انتقال را ارسال کنید!"
                                 , reply_markup=keyboard)
            await state.set_state(Change.waiting_for_photo)  # وضعیت برای دریافت ساعت
    except ValueError:
        # اگر ورودی عددی نبود
        await message.answer("⛔ لطفاً فقط عدد وارد کنید.")
        await state.set_state(Change.waiting_for_amount)  # وضعیت برای دریافت مبلغ


@router.message(Change.waiting_for_photo)
async def get_time(message: types.Message, state: FSMContext):
    # دریافت تصویر از پیام کاربر
    if message.text:
        await message.answer("⛔ لطفا فقط تصویر رسید انتقال را بدون متن ارسال کنید!")
        await state.set_state(Change.waiting_for_photo)  # وضعیت برای دریافت مبلغ
        return

    transfer_photo = message.photo[-1].file_id
    await state.update_data(transfer_photo=transfer_photo)  # ذخیره تصویر در وضعیت

    # دریافت مبلغ و ساعت از وضعیت
    user_data = await state.get_data()
    amount = user_data.get("amount")
    amount_formatted = "{:,.0f}".format(amount)


    # ارسال پیام تایید دریافت اطلاعات
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید", callback_data="confirm_transfer")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
        ]
    )
    await message.answer_photo(
        photo=transfer_photo,
        caption=(
            f"💵 مبلغ :\n{amount_formatted} ریال\n"
            f"درج شده در رسید انتقال!\n\n"
            "🚨 لطفاً دقت داشته باشید مبلغ ارسالی باید به ریال و مطابق با رسید تراکنش باشد.\n"
            "در غیر این صورت، رسید شما رد خواهد شد.\n\n"
            "برای تکمیل فرآیند، دکمه «تأیید» را فشار دهید."
        ),
        reply_markup=keyboard
    )
    return


@router.callback_query(F.data == "confirm_transfer")
async def confirm_transfer(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):


    user_data = await state.get_data()
    transfer_photo = user_data.get("transfer_photo")
    amount = user_data.get("amount") / 10
    card_number = user_data.get("card_number")
    card_number = str(card_number)
    card_number = "صادرات" if "0981" in card_number else "بلو" if "9591" in card_number else ""

    amount_formatted = "{:,.0f}".format(amount)


    if callback_query.from_user.username:
        user_info = f"@{callback_query.from_user.username}"
    else:
        user_info = f"<a href='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.id}</a>"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید رسید پرداخت", callback_data="confirm_amount")],
            [InlineKeyboardButton(text="❌ رد رسید پرداخت", callback_data="reject_transfer")]
        ]
    )

    text = (
        "🛠️ تراکنش جدید!\n\n"
        f"👤 کاربر:\n{user_info}\n"
        f"🆔 آیدی عددی:\n<code>{callback_query.from_user.id}</code>\n"
        f"💰 مبلغ پرداخت شده:\n{amount_formatted} تومان\n"
        f"\n{card_number}"
    )

    await callback_query.message.delete()
    await callback_query.message.answer(
        "✅ رسید شما دریافت و در حال بررسی است.\n\n"
        "رسیدها روزانه به‌صورت گروهی و در زمان مشخص بررسی می‌شوند.\n"
        "لطفاً تا تأیید نهایی صبور باشید.\n\n"
        "🙏 از اعتماد شما سپاسگزاریم."
    )

    await bot.send_photo(photo=transfer_photo, chat_id=check_gp, caption=text, reply_markup=keyboard, parse_mode="HTML")
    await state.clear()



@router.callback_query(F.data == "confirm_amount")
async def search_and_update_wallet(callback_query: types.CallbackQuery, state: FSMContext):
    text = callback_query.message.caption or callback_query.message.text

    # user_id
    user_id_match = re.search(r"🆔 آیدی عددی:\s*(\d+)", text)
    user_id = int(user_id_match.group(1))

    # amount
    amount_match = re.search(r"💰 مبلغ پرداخت شده:\s*([\d,]+)", text)
    amount = int(amount_match.group(1).replace(",", ""))

    amount_formatted = "{:,.0f}".format(amount)


    username = user_id
    user_file = None
    wallet_balance = 0

    for user_dir in os.listdir("Data_csv"):
        user_path = os.path.join("Data_csv", user_dir, f"{user_dir}.csv")

        if os.path.exists(user_path):
            df = pd.read_csv(user_path, encoding="utf-8")
            if "wallet" not in df.columns or "id" not in df.columns or "username" not in df.columns:
                await callback_query.answer("❌ فایل داده‌ها ناقص است.")
                return

            df["wallet"] = df["wallet"].iloc[0]

            user_row = df[df["id"] == username]

            if not user_row.empty:
                user_file = user_path

                wallet_balance = user_row["wallet"].iloc[0]
                break



    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید مبلغ", callback_data="deposit_amount")],
            [InlineKeyboardButton(text="❌ رد رسید پرداخت", callback_data="reject_transfer")]
        ]
    )


    # فرمت‌کردن موجودی به صورت مبلغ بدون اعشار
    wallet_balance_formatted = "{:,.0f}".format(wallet_balance)

    await state.update_data(user_file=user_file, wallet_balance=wallet_balance, username=username, amount=amount)
    await callback_query.message.edit_caption(caption=f"🔹 موجودی فعلی:\n {wallet_balance_formatted} تومان\n"
                                              f" مبلغ {amount_formatted} تومان "
                                              f"\nبه کیف پول کاربر اضافه خواهد شد."
                                              f"\nآیا تایید میکنید؟"
                                              , reply_markup=keyboard)



@router.callback_query(F.data == "deposit_amount")
async def update_wallet_balance(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):

    user_data = await state.get_data()
    user_file = user_data.get("user_file")
    amount = user_data.get("amount")
    wallet_balance = user_data.get("wallet_balance")

    new_balance = wallet_balance + amount
    username = user_data.get("username")
    df = pd.read_csv(user_file, encoding="utf-8")

    df["wallet"] = new_balance
    df.to_csv(user_file, index=False, encoding="utf-8")
    new_balance_formatted = "{:,.0f}".format(new_balance)
    amount_formatted = "{:,.0f}".format(amount).lstrip("-")

    await callback_query.message.edit_caption(
        caption=(
            f"👤 کاربر: <code>{username}</code>\n\n"
            f"✅ مبلغ {amount_formatted} تومان\n"
            f"به کیف پول کاربر اضافه شد.\n"
            f"💰 موجودی جدید:\n"
            f" {new_balance_formatted} تومان"
        ),
        parse_mode="HTML"
    )

    await bot.send_message(chat_id=df["id"],
                           text=f"✅ مبلغ {amount_formatted}"
                                f" تومان به کیف پول شما توسط ادمین اضافه شد.\n"
                                f" موجودی جدید:\n"
                                f"{new_balance_formatted} تومان ")


    await state.clear()


@router.callback_query(F.data == "reject_transfer")
async def rejection(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        message_id = callback_query.message.message_id
        photo = callback_query.message.photo[-1].file_id
        text = callback_query.message.caption

        user_id_match = re.search(r"🆔 آیدی عددی:\s*(\d+)", text)
        user_name = re.search(r"@([\w\d_]+)", text)



        user_id = user_id_match.group(1) if user_id_match else "نامشخص"
        user_name = user_name.group(1) if user_name else "نامشخص"



        msg = await callback_query.message.answer("لطفا دلیل رد درخواست را بنویسید:")
        bot_message_id = msg.message_id

        await state.set_state(Change.waiting_rejection_reason)
        await state.update_data(user_id=user_id, user_name=user_name, photo=photo,
                                message_id=message_id, bot_message_id=bot_message_id)

    except Exception as e:
        await callback_query.message.answer(f"⛔ خطا در رد درخواست:\n{e}")


@router.message(Change.waiting_rejection_reason)
async def process_rejection_reason(message: types.Message, state: FSMContext, bot: Bot):


    # دریافت یادداشت از پشتیبانی

    rejection_reason = message.text.strip()

    # گرفتن داده‌ها از FSM
    user_data = await state.get_data()

    user_id = user_data.get("user_id")
    user_name = user_data.get("user_name")
    photo = user_data.get("photo")
    message_id = user_data.get("message_id")
    bot_message_id = user_data.get("bot_message_id")

    await bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)


    # await message.delete(message_id=bot_message_id)
    # await message.delete(message_id=message_id)

    await message.answer_photo(
        photo=photo,
        caption=(
            f"❌ درخواست شارژ رد شد!\n"
            f"👨‍💼 رد شده توسط: <code>{message.from_user.id}</code>\n\n"
            f"👤 کاربر:\n@{user_name} (ID: <code>{user_id}</code>)\n"
            f"📅 دلیل رد درخواست:\n{rejection_reason}\n"
        ),
        parse_mode="HTML"
    )

    # ارسال پیام به کاربر مبنی بر رد شدن تمدید همراه با یادداشت
    await bot.send_message(
        user_id,
        f"❌ رسید پرداخت شما رد شد.\n\n"
        f"📜 دلیل رد:\n{rejection_reason}\n\n"
        "در صورت بروز اشتباه، لطفاً با پشتیبانی در تماس باشید."
    )


    await message.delete()
    # پاک کردن داده‌های FSM
    await state.clear()

