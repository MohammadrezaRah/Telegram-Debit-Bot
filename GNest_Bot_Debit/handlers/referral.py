from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F, Bot, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import pandas as pd

router = Router()


@router.message(F.text == "👥🎁 زیرمجموعه و پاداش")
async def referral_main_menu(message: types.Message):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧷 لینک دعوت من", callback_data="show_referral_link")],
        [InlineKeyboardButton(text="💵 درخواست برداشت", callback_data="withdrawal_req")],
        [InlineKeyboardButton(text="👥 زیرمجموعه‌های من", callback_data="my_referrals")]
    ])

    await message.answer(
        "🎁👥 به بخش ریفرال خوش آمدید!"
        "\n"
        "\nاز طریق دکمه‌های زیر می‌تونید زیرمجموعه‌هاتون رو ببینید یا لینک اختصاصی‌تون رو بردارید."
        "\n"
        "\n🔹 به صورت مادام العمر به ازای هر خرید زیرمجموعه، **۸٪ مبلغ خرید** به کیف پول شما اضافه میشه."
        "\n🔹 این مبلغ قابل استفاده در خرید سرویس از ربات هست."
        "\n🔹 و وقتی موجودی‌تون به **۱۰۰,۰۰۰ تومان** برسه، می‌تونید درخواست برداشت به حساب بانکی‌تون بدید. 💸",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "back_to_referral_menu")
async def back_to_referral_menu(callback: types.CallbackQuery):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧷 لینک دعوت من", callback_data="show_referral_link")],
        [InlineKeyboardButton(text="💵 درخواست برداشت", callback_data="withdrawal_req")],
        [InlineKeyboardButton(text="👥 زیرمجموعه‌های من", callback_data="my_referrals")]
    ])

    await callback.message.edit_text("🎁👥 به بخش ریفرال برگشتید!", reply_markup=keyboard)


@router.callback_query(F.data == "show_referral_link")
async def show_referral_link(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    referral_link = f"https://t.me/{(await callback.bot.me()).username}?start=ref_{user_id}"

    await callback.answer()
    await callback.message.answer(
        f"📎 اینم لینک اختصاصی شما برای دعوت دوستان:\n\n{referral_link}\n\n"
        "💰 با ارسال این لینک، به ازای هر خرید زیرمجموعه، ۹٪ پورسانت دریافت می‌کنید!\n"
        "📤 لینک رو بفرست و درآمد کسب کن!"
    )


@router.callback_query(F.data == "withdrawal_req")
async def withdrawal_request(callback: types.CallbackQuery, bot: Bot):
    await callback.answer()
    user_id = callback.from_user.id
    file_path = f"Data_csv/{user_id}/{user_id}.csv"

    if not os.path.exists(file_path):
        await callback.message.answer("❌ حساب شما پیدا نشد."
                                      "لطفا از گزینه /start استفاده کنید")
        return

    df = pd.read_csv(file_path)
    wallet = int(df.loc[0, "wallet"])

    if wallet >= 100000:
        await callback.message.edit_text(
            "✅ درخواست برداشت شما با موفقیت ثبت شد.\n"
            "در اسرع وقت از طریق پشتیبانی با شما تماس گرفته خواهد شد. 💸"
        )
        await bot.send_message(
            7543863141,
            f"""
            👤 کاربر زیر قصد برداشت مبلغی از کیف پول خود را دارد:

        🔹 نام:    {callback.from_user.full_name}
🔹 یوزرنیم:            {f"@{callback.from_user.username}" if callback.from_user.username else
            f"<a href='tg://user?id={callback.from_user.id}'>{callback.from_user.id}</a>"}
            🆔 آیدی عددی: <code>{callback.from_user.id}</code>
            """,
            parse_mode="HTML"
        )

    else:
        await callback.message.answer(
            f"⚠️ موجودی شما برای برداشت کافی نیست.\n"
            f"💰 موجودی فعلی: {wallet:,} تومان\n"
            f"🔒 حداقل برای برداشت: 100,000 تومان"
        )


@router.callback_query(F.data == "my_referrals")
async def callback_my_referrals(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    directory = f"Data_csv/{user_id}"
    referrals_path = os.path.join(directory, "referrals_buy.csv")


    if os.path.exists(referrals_path):
        df = pd.read_csv(referrals_path)

        total = int(df["total_ref"].iloc[0])
        buy_count = int(df["buy_count"].iloc[0])
        earning = int(df["earning"].iloc[0])

        text = f"""📊 وضعیت زیرمجموعه‌ها:

🔸 تعداد کل زیرمجموعه‌ها : {total}
🔸 تعداد خرید های انجام شده : {buy_count}
🔸 مجموع کسب در آمد از زیر مجموعه ها : {earning:,}


برای مشاهده‌ی جزئیات یا بازگشت، دکمه زیر را بزنید 👇
"""
    else:
        text = "❌ شما هنوز هیچ زیرمجموعه‌ای دعوت نکردید."
        await callback.message.edit_text(text)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 جزئیات زیرمجموعه‌ها", callback_data="referral_details")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_referral_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "referral_details")
async def referral_details(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    directory = f"Data_csv/{user_id}"
    referrals_path = os.path.join(directory, "referrals.csv")

    if os.path.exists(referrals_path):
        df = pd.read_csv(referrals_path)
        if df.empty:
            text = "❌ شما هیچ زیرمجموعه‌ای ندارید."
        else:
            text = "📋 لیست زیرمجموعه‌های شما:\n\n"
            for i, row in df.iterrows():
                user_id = row["user_id"]
                username = row['username'] if pd.notna(row['username']) else "_"
                username = f"<a href='tg://user?id={user_id}'>{user_id}</a>" \
                    if username == "_" else username
                user_name = row['user_name'] if pd.notna(row['user_name']) else "-"
                buy_count = int(row['buy_count']) if pd.notna(row['buy_count']) else 0
                text += f"{i+1}. {user_name} (@{username})\n🛒 تعداد خرید: {buy_count}\n\n"
    else:
        text = "❌ شما هیچ زیرمجموعه‌ای ندارید."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="my_referrals")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)



