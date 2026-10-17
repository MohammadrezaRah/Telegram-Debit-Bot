from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import pandas as pd

router = Router()


class Change(StatesGroup):
    waiting_for_name1 = State()
    waiting_for_amount1 = State()





@router.message(F.text == "موجودی کیف پول دستی")
async def request_username(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )
    await message.answer("یوزرنیم مورد نظر یا شماره آیدی کاربر را وارد کنید:", reply_markup=keyboard)
    await state.set_state(Change.waiting_for_name1)


@router.message(Change.waiting_for_name1)
async def search_and_update_wallet(message: Message, state: FSMContext):
    username = message.text.strip()
    username = username if "@" not in username else username.lstrip("@")
    user_found = False
    user_file = None
    wallet_balance = 0

    for user_dir in os.listdir("Data_csv"):
        user_path = os.path.join("Data_csv", user_dir, f"{user_dir}.csv")

        if os.path.exists(user_path):
            df = pd.read_csv(user_path, encoding="utf-8")
            if "wallet" not in df.columns or "id" not in df.columns or "username" not in df.columns:
                await message.answer("❌ فایل داده‌ها ناقص است.")
                return

            df["wallet"] = df["wallet"].iloc[0]

            # تغییر در بررسی اینکه آیا شناسه یا یوزرنیم است
            if username.isdigit():
                df["id"] = df["id"].astype(str)  # تبدیل ID به str برای مقایسه صحیح
                user_row = df[df["id"] == username]
            else:
                user_row = df[df["username"] == username]

            if not user_row.empty:
                user_found = True
                user_file = user_path

                wallet_balance = df["wallet"].iloc[0]
                break

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )

    if not user_found:
        await message.answer("❌ یوزرنیم یا آیدی مورد نظر یافت نشد. لطفاً دوباره تلاش کنید:", reply_markup=keyboard)
        await state.set_state(Change.waiting_for_name1)
        return

    # فرمت‌کردن موجودی به صورت مبلغ بدون اعشار
    wallet_balance_formatted = "{:,.0f}".format(wallet_balance)

    await state.update_data(user_file=user_file, wallet_balance=wallet_balance, username=username)
    await message.answer(f"🔹 موجودی فعلی کیف پول: {wallet_balance_formatted} تومان\n"
                         "لطفاً مقدار تغییر موجودی را به تومان وارد کنید:\n"
                         "برای کم کردن از موجودی عدد منفی وارد کنید مانند: \n -90000", reply_markup=keyboard)
    await state.set_state(Change.waiting_for_amount1)


@router.message(Change.waiting_for_amount1)
async def update_wallet_balance(message: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    user_file = user_data.get("user_file")
    wallet_balance = user_data.get("wallet_balance")
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ لطفاً مقدار معتبر(فقط عدد) وارد کنید.")
        await state.set_state(Change.waiting_for_amount1)
        return
    new_balance = wallet_balance + amount
    username = user_data.get("username")
    df = pd.read_csv(user_file, encoding="utf-8")

    df["wallet"] = new_balance
    df.to_csv(user_file, index=False, encoding="utf-8")
    new_balance_formatted = "{:,.0f}".format(new_balance)
    amount_formatted = "{:,.0f}".format(amount).lstrip("-")

    try:


        if amount == 0:
            await message.answer("❌ مقدار وارد شده نمیتواند عدد صفر باشد.")
            return
        elif amount > 0:
            await message.answer(
                f"✅ مبلغ {amount_formatted} تومان به کیف پول {username} "
                f"با موفقیت اضافه شد. موجودی جدید: {new_balance_formatted} تومان")
            await bot.send_message(chat_id=df["id"],
                                   text=f"✅ مبلغ {amount_formatted}"
                                        f" تومان به کیف پول شما توسط ادمین اضافه شد. موجودی جدید: "
                                        f"{new_balance_formatted} تومان ")
        elif amount < 0:
            await message.answer(
                f"✅ مبلغ {amount_formatted} تومان از کیف پول {username} "
                f" با موفقیت کسر شد. موجودی جدید: {new_balance_formatted} تومان")
            await bot.send_message(chat_id=df["id"],
                                   text=f"✅ مبلغ {amount_formatted}"
                                        f" تومان از کیف پول شما توسط ادمین کسر شد. موجودی جدید: "
                                        f"{new_balance_formatted} تومان ")

    except ValueError:
        await message.answer("❌ لطفاً مقدار معتبر(عدد) وارد کنید.")
        await state.set_state(Change.waiting_for_amount1)
        return
    await state.clear()
