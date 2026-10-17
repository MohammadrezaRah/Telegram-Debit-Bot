from aiogram import types, Router, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

support_chat_id = 1574768588  # آیدی پشتیبانی


# تعریف State برای دریافت پیام پشتیبان
class SupportState(StatesGroup):
    waiting_for_message = State()
    waiting_for_reply = State()


@router.message(F.text == "☎️ تماس با ما")
async def support_command(message: types.Message):
    inlinekeyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # [InlineKeyboardButton(text="❓ سوالات متداول", callback_data="faq")],
            [InlineKeyboardButton(text="📞 تماس مستقیم با پشتیبانی", callback_data="contact_support")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )
    await message.answer("شما وارد بخش پشتیبانی شدید. لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                         reply_markup=inlinekeyboard)


@router.callback_query(F.data == "faq")
async def faq_query(callback_query: types.CallbackQuery):
    await callback_query.answer("در اینجا سوالات متداول شما نمایش داده می‌شود.")


@router.callback_query(F.data == "contact_support")
async def contact_support_query(callback_query: types.CallbackQuery, state: FSMContext):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
    )
    await callback_query.message.answer("لطفاً پیام خود را ارسال کنید تا به پشتیبانی منتقل شود.",
                                        reply_markup=reply_markup)

    await state.set_state(SupportState.waiting_for_message)


@router.message(SupportState.waiting_for_message)
async def forward_support_message(message: types.Message, state: FSMContext, bot: Bot):

    # ذخیره آیدی کاربر برای ارسال پاسخ بعداً
    await state.update_data(user_id=message.chat.id)

    # ایجاد دکمه شیشه‌ای برای ارسال پاسخ
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 ارسال پاسخ", callback_data=f"reply_{message.chat.id}")],
        ]
    )

    if message.text:
        await bot.send_message(
            support_chat_id,
            f"""
            📩 پیام جدید از:
            🔹 نام:{message.from_user.full_name}
        🔹 یوزرنیم:    {f"@{message.from_user.username}" if message.from_user.username else 
            f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>"}
            🆔 آیدی عددی: <code>{message.from_user.id}</code>
            
                             
            ✉️ متن پیام:
            {message.text}
            """,
            reply_markup=reply_markup, parse_mode="HTML"
        )
    else:
        # فوروارد پیام‌های غیر متنی
        await message.forward(support_chat_id)

        await bot.send_message(
            support_chat_id,
            f"""
            📩 پیام جدید از:
            🔹 نام:{message.from_user.full_name}
        🔹 یوزرنیم:    {f"@{message.from_user.username}" if message.from_user.username else 
            f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>"}
            🆔 آیدی عددی: <code>{message.from_user.id}</code>
            """,
            reply_markup=reply_markup, parse_mode="HTML"
        )

    await message.answer("پیام شما به پشتیبانی ارسال شد. لطفاً منتظر پاسخ باشید.")
    await state.clear()


@router.callback_query(F.data.startswith("reply_"))
async def ask_support_reply(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])  # استخراج آیدی کاربر
    await state.update_data(reply_to=user_id)
    await callback_query.message.answer("✍ لطفاً پاسخ خود را تایپ و ارسال کنید.")
    await state.set_state(SupportState.waiting_for_reply)


@router.message(SupportState.waiting_for_reply)
async def send_reply_to_user(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("reply_to")

    if user_id:
        reply_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                # [InlineKeyboardButton(text="❓ سوالات متداول", callback_data="faq")],
                [InlineKeyboardButton(text="📤 ارسال پاسخ", callback_data="contact_support")],
            ]
        )
        if message.text:
            await bot.send_message(user_id, f"📩 پیام از پشتیبانی:\n\n{message.text}",
                                   reply_markup=reply_keyboard)
        else:
            await message.forward(user_id)
            await bot.send_message(user_id, f"📩 پیام از پشتیبانی\n\n",
                                   reply_markup=reply_keyboard)
        await message.answer("✅ پاسخ شما ارسال شد.")
    else:
        await message.answer("❌ خطا: آیدی کاربر یافت نشد.")

    await state.clear()
