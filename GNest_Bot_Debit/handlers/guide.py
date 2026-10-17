from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

router = Router()


@router.message(lambda message: message.text == "📖 آموزش")
async def show_guide_options(message: types.Message):
    # ساخت کیبورد شیشه‌ای
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="V2Ray | وی تو ری", callback_data="show_v2ray_guide")],
            [InlineKeyboardButton(text="OpenVpn | اوپن وی پی ان", callback_data="show_ovpn_guide")],
        ]
    )

    # ارسال پیام با کیبورد
    await message.answer("لطفاً سیستم عامل خود را انتخاب کنید:", reply_markup=keyboard)


@router.callback_query(F.data == "show_guide")
async def show_guide(callback_query: types.CallbackQuery):
    # ساخت کیبورد شیشه‌ای
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="V2Ray | وی تو ری", callback_data="show_v2ray_guide")],
            [InlineKeyboardButton(text="OpenVpn | اوپن وی پی ان", callback_data="show_ovpn_guide")],
        ]
    )

    # ارسال پیام با کیبورد
    await callback_query.message.answer("لطفاً سیستم عامل خود را انتخاب کنید:", reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data == "show_ovpn_guide")
async def show_guide(callback_query: types.CallbackQuery):
    # ساخت کیبورد شیشه‌ای
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 اندروید", callback_data="android_ovpn_guide")],
            [InlineKeyboardButton(text="🍏 آی او اس", callback_data="ios_ovpn_guide")],
            [InlineKeyboardButton(text="💻 ویندوز", callback_data="windows_ovpn_guide")]
        ]
    )

    # ارسال پیام با کیبورد
    await callback_query.message.edit_text("لطفاً سیستم عامل خود را انتخاب کنید:", reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data == "show_v2ray_guide")
async def show_guide(callback_query: types.CallbackQuery):
    # ساخت کیبورد شیشه‌ای
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 اندروید", callback_data="android_v2ray_guide")],
            [InlineKeyboardButton(text="🍏 آی او اس", callback_data="ios_v2ray_guide")],
            [InlineKeyboardButton(text="💻 ویندوز", callback_data="windows_v2ray_guide")]
        ]
    )

    # ارسال پیام با کیبورد
    await callback_query.message.edit_text("لطفاً سیستم عامل خود را انتخاب کنید:", reply_markup=keyboard)



@router.callback_query(lambda c: c.data == "android_v2ray_guide")
async def android_guide(callback_query: types.CallbackQuery):
    # لینک یوتیوب برای اندروید
    youtube_link = "https://youtube.com/shorts/DeJjRMRnzjw?si=fw6_YgDeE75J_pnv"
    await callback_query.message.edit_text(f"برای مشاهده آموزش اندروید، به این لینک مراجعه کنید: {youtube_link}")
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "android_ovpn_guide")
async def android_guide(callback_query: types.CallbackQuery):
    # لینک یوتیوب برای اندروید
    youtube_link = "https://youtube.com/shorts/DeJjRMRnzjw?si=fw6_YgDeE75J_pnv"
    await callback_query.message.edit_text(f"برای مشاهده آموزش اندروید، به این لینک مراجعه کنید: {youtube_link}")
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "ios_v2ray_guide")
async def ios_guide(callback_query: types.CallbackQuery):
    # لینک یوتیوب برای آی او اس
    youtube_link = "https://www.youtube.com/watch?v=your_ios_video_link"
    await callback_query.message.edit_text(f"برای مشاهده آموزش آی او اس، به این لینک مراجعه کنید: {youtube_link}")
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "ios_ovpn_guide")
async def ios_guide(callback_query: types.CallbackQuery):
    # لینک یوتیوب برای آی او اس
    youtube_link = "https://www.youtube.com/watch?v=your_ios_video_link"
    await callback_query.message.edit_text(f"برای مشاهده آموزش آی او اس، به این لینک مراجعه کنید: {youtube_link}")
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "windows_v2ray_guide")
async def windows_guide(callback_query: types.CallbackQuery):
    # لینک یوتیوب برای ویندوز
    youtube_link = "https://www.youtube.com/watch?v=your_windows_video_link"
    await callback_query.message.edit_text(f"برای مشاهده آموزش ویندوز، به این لینک مراجعه کنید: {youtube_link}")
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "windows_ovpn_guide")
async def windows_guide(callback_query: types.CallbackQuery):
    # لینک یوتیوب برای ویندوز
    youtube_link = "https://www.youtube.com/watch?v=your_windows_video_link"
    await callback_query.message.edit_text(f"برای مشاهده آموزش ویندوز، به این لینک مراجعه کنید: {youtube_link}")
    await callback_query.answer()
