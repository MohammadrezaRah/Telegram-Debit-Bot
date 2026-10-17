import os
import pandas as pd
from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, CommandObject

router = Router()

support_id = [841997231, 7543863141, 1574768588]

reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 خرید")],
        [KeyboardButton(text="🛍️ اقساط من")],
        [KeyboardButton(text="💳 کیف پول و شارژ"), KeyboardButton(text="👥🎁 زیرمجموعه و پاداش")],
        [KeyboardButton(text="📜 قوانین")],
        [KeyboardButton(text="☎️ تماس با ما")]
    ],
    resize_keyboard=True
)

inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🌐 وبسایت",
                              url="https://www.game-nest.ir")],
        [InlineKeyboardButton(text="📢 کانال تلگرام", url="https://t.me/game_nest_babol")],
    ]
)

special_key = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⛔ بستن فروش"), KeyboardButton(text="✅ باز کردن فروش")],
        [KeyboardButton(text="موجودی کیف پول دستی")],
        [KeyboardButton(text="ارسال پیام به کاربران"), KeyboardButton(text="مشاهده اطلاعات کاربر")],
        [KeyboardButton(text="فروشنده ها")],

        [KeyboardButton(text="🛒 خرید")],
        [KeyboardButton(text="🛍️ اقساط من")],
        [KeyboardButton(text="💳 کیف پول و شارژ"), KeyboardButton(text="👥🎁 زیرمجموعه و پاداش")],
        [KeyboardButton(text="📜 قوانین")],
        [KeyboardButton(text="☎️ تماس با ما")]
    ],
    resize_keyboard=True
)



@router.message(F.text == "/start")
async def start_command(message: types.Message, bot: Bot):

    support = message.chat.id in support_id
    keyboard = special_key if support else reply_keyboard


    await message.answer("👋 سلام به ربات <b>GameNest</b> خوش آمدید.\n\n"
                         "شما میتوانید از طریق این ربات:\n"
                         "محصولات ما را به صورت اقساط٬"
                         " بدون نیاز به چک ٬ سفته و یا ضامن خریداری کنید!",
                         reply_markup=inline_keyboard, parse_mode="HTML")
    await message.answer("⚠️ لطفا قبل از خرید، قوانین ربات را مطالعه کنید.\n\n"
                         f"🆔 آیدی شما: <code>{message.from_user.id}</code>",
                         reply_markup=keyboard, parse_mode="HTML")


    directory = f"Data_csv/{message.chat.id}"
    file_path = os.path.join(directory, f"{message.chat.id}.csv")

    if os.path.exists(file_path):
        print("فایل وجود دارد.")
    else:
        await bot.send_message(
            chat_id=1574768588,
            text=f"""
            👤 کاربر جدید ثبت‌نام کرد:

        🔹 نام:    {message.from_user.full_name}
        🔹 یوزرنیم:    {f"@{message.from_user.username}" if message.from_user.username else 
            f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>"}
            🆔 آیدی عددی: <code>{message.from_user.id}</code>
            """,
            parse_mode="HTML"
        )
        print("فایل وجود ندارد.")
        create_csv(message.chat.id, message.chat.username)  # فرض کنید این تابع تغییر داده شده باشد



@router.message(CommandStart(deep_link=True))
async def start_command(message: types.Message, bot: Bot, command: CommandObject):

    support = message.chat.id in support_id
    keyboard = special_key if support else reply_keyboard

    deep_link = command.args  # مثلاً "ref_123456"

    referral_id = None
    if deep_link and deep_link.startswith("ref_"):
        try:
            referral_id = int(deep_link.split("_")[1])
        except:
            referral_id = None
    directory = f"Data_csv/{message.chat.id}"
    file_path = os.path.join(directory, f"{message.chat.id}.csv")

    if message.chat.id == referral_id:
        if support:
            await message.answer("⛔ شما نمیتوانید زیر مجموعه ی خودتان باشید!!",
                                 reply_markup=keyboard)
        else:
            await message.answer("⛔ شما نمیتوانید زیر مجموعه ی خودتان باشید!!",
                                 reply_markup=keyboard)
        return

    if not os.path.exists(file_path):

        await message.answer("👋 سلام به ربات <b>GameNest</b> خوش آمدید.\n\n"
                             "شما میتوانید از طریق این ربات:\n"
                             "محصولات ما را به صورت اقساط٬"
                             " بدون نیاز به چک ٬ سفته و یا ضامن خریداری کنید!",
                             reply_markup=inline_keyboard, parse_mode="HTML")
        await message.answer("⚠️ لطفا قبل از خرید، قوانین ربات را مطالعه کنید.\n\n"
                             f"🆔 آیدی شما: <code>{message.from_user.id}</code>",
                             reply_markup=keyboard, parse_mode="HTML")


        await bot.send_message(
            chat_id=1574768588,
            text=f"""
            👤 کاربر جدید ثبت‌نام کرد:

        🔹 نام:    {message.from_user.full_name}
        🔹 یوزرنیم:    {f"@{message.from_user.username}" if message.from_user.username else 
            f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>"}
            🆔 آیدی عددی: <code>{message.from_user.id}</code>
            """,
            parse_mode="HTML"
        )
        create_csv(message.chat.id, message.chat.username, referral_id)


        if referral_id:
            username_text = f"@{message.from_user.username}" if message.from_user.username else\
                f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>"
            await bot.send_message(
                referral_id,
                text=(
                    f"🎉 کاربر {message.from_user.full_name} "
                    "از طریق لینک اختصاصی شما به عنوان زیرمجموعه در ربات ثبت‌نام کرد!"
                    f"\n\n🔹 دیدن کاربر: {username_text} "
                ),
                parse_mode="HTML"
            )

            save_to_referral_file(referral_id, message.chat.id, message.from_user.username, message.from_user.full_name)
        return

    else:

        await message.answer("⛔ شما قبلا ثبت نام کرده اید و نمیتوانید زیر مجموعه ی دیگران باشید!!",
                             reply_markup=keyboard)


def create_csv(ID, username, referral_id=None):
    columns = ["username", "id", "law", "wallet", "debts", "remainder", "referral"]
    data = [[username, ID, False, 0, 0, 0, referral_id]]
    directory = f"Data_csv/{ID}"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{ID}.csv")
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(file_path, index=False, encoding="utf-8")



def save_to_referral_file(referrer_id, new_user_id, new_username, new_user_name):
    directory = f"Data_csv/{referrer_id}"
    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, "referrals.csv")

    data = {"user_id": [new_user_id], "username": [new_username], "user_name": [new_user_name], "buy_count": 0}
    new_df = pd.DataFrame(data)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if not (df["user_id"] == new_user_id).any():
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            print("از قبل ثبت شده بود")
            return
    else:
        df = new_df
    df.to_csv(file_path, index=False, encoding="utf-8")


    buy_file_path = os.path.join(directory, "referrals_buy.csv")
    buy_file_data = {"total_ref": [1], "buy_count": [0], "earning": [0]}
    new_df_buy = pd.DataFrame(buy_file_data)
    if os.path.exists(buy_file_path):
        buy_df = pd.read_csv(buy_file_path)
        total = int(buy_df["total_ref"].iloc[0]) + 1
        buy_df["total_ref"] = [total]
    else:
        buy_df = new_df_buy
    buy_df.to_csv(buy_file_path, index=False, encoding="utf-8")

    print(f"کاربر {new_user_id} به referrals {referrer_id} اضافه شد.")


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback_query: types.CallbackQuery, state: FSMContext):

    await state.clear()

    support = callback_query.from_user.id in support_id
    keyboard = special_key if support else reply_keyboard

    text = "✅ به منوی اصلی بازگشتید!"

    # اگر پیام عکس بود
    if callback_query.message.photo:
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=text,
            reply_markup=inline_keyboard
        )
    else:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=inline_keyboard
        )

    await callback_query.message.answer(
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )


@router.message(F.text == "🔙 بازگشت")
async def back_to_main_text(message: types.Message, state: FSMContext):

    support = message.chat.id in support_id
    keyboard = special_key if support else reply_keyboard

    await state.clear()
    await message.answer("✅ به منوی اصلی بازگشتید!",
                         reply_markup=inline_keyboard)
    await message.answer("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=keyboard)

