from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
import pandas as pd
import os

router = Router()


# وضعیت‌ها
class BroadcastState(StatesGroup):
    choosing_target = State()
    entering_user_id = State()
    entering_message = State()


# شروع ارسال پیام
@router.message(F.text.lower() == "ارسال پیام به کاربران")
async def start_broadcast(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="برای یک نفر")],
            [KeyboardButton(text="برای همه")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(BroadcastState.choosing_target)
    await message.answer("می‌خوای برای یک نفر بفرستی یا برای همه؟", reply_markup=keyboard)


# انتخاب حالت ارسال
@router.message(BroadcastState.choosing_target)
async def choose_target(message: Message, state: FSMContext):
    if message.text == "برای یک نفر":
        await state.set_state(BroadcastState.entering_user_id)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🔙 بازگشت")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("لطفاً آیدی عددی یا یوزر نیم کاربر رو وارد کن:", reply_markup=keyboard)
    elif message.text == "برای همه":
        await state.update_data(target="all")
        await state.set_state(BroadcastState.entering_message)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🔙 بازگشت")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("متن پیامت رو بنویس:", reply_markup=keyboard)
    else:
        await message.answer("لطفاً یکی از گزینه‌ها رو انتخاب کن.")


# گرفتن آیدی کاربر
@router.message(BroadcastState.entering_user_id)
async def get_user_id(message: Message, state: FSMContext):
    await state.update_data(target="one", user_id=message.text)
    await state.set_state(BroadcastState.entering_message)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("متن پیامت رو بنویس:", reply_markup=keyboard)


@router.message(BroadcastState.entering_message)
async def send_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    text = message.text
    base_path = './Data_csv'


    if data["target"] == "one":
        user_identifier = data["user_id"]
        try:
            user_found = False
            username = user_identifier.lstrip('@') if "@" in user_identifier else user_identifier
            for user_dir in os.listdir("Data_csv"):
                user_path = os.path.join("Data_csv", user_dir, f"{user_dir}.csv")

                if os.path.exists(user_path):
                    df = pd.read_csv(user_path, encoding="utf-8")

                    if "id" not in df.columns or "username" not in df.columns:
                        await message.answer("❌ فایل داده‌ها ناقص است.")
                        return

                    # تغییر در بررسی اینکه آیا شناسه یا یوزرنیم است
                    if username.isdigit():
                        df["id"] = df["id"].astype(str)  # تبدیل ID به str برای مقایسه صحیح
                        user_row = df[df["id"] == username]
                    else:
                        user_row = df[df["username"] == username]

                    if not user_row.empty:
                        user_found = True
                        chat_id = int(user_row["id"].iloc[0])
                        break

            if not user_found:
                await message.answer("❌ یوزرنیم یا آیدی مورد نظر یافت نشد. لطفاً دوباره تلاش کنید:",
                                     reply_markup=keyboard)
                await state.set_state(BroadcastState.entering_message)
                return
            await message.bot.send_message(chat_id=chat_id, text=text)
            await message.answer("پیام برای کاربر ارسال شد.")

        except Exception as e:
            await message.answer(f"ارسال پیام ناموفق بود: {e}")

    else:
        sent = 0
        failed = 0
        for folder_name in os.listdir(base_path):
            if folder_name.isdigit():
                try:
                    await message.bot.send_message(chat_id=int(folder_name), text=text)
                    sent += 1
                except:
                    failed += 1
        await message.answer(f"✅ پیام برای {sent} کاربر ارسال شد.\n❌ شکست خورده: {failed}")

    await state.clear()
