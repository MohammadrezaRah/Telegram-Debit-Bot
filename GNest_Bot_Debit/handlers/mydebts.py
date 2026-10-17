import os
import re
import pandas as pd
import jdatetime
from datetime import date
import json

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


class Change(StatesGroup):
    waiting_for_debt_photo = State()


@router.message(F.text == "🛍️ اقساط من")
async def show_debts(message: Message):
    user_id = message.chat.id

    # مسیر فایل CSV مربوط به سفارش های کاربر
    user_folder = f"Data_csv/{user_id}"
    os.makedirs(user_folder, exist_ok=True)
    csv_file = os.path.join(user_folder, "installment_purchases.csv")

    # بررسی اینکه فایل CSV وجود دارد یا نه
    if not os.path.exists(csv_file):
        await message.answer("❌ هیچ قسطی برای پرداخت یافت نشد.")
        return

    # خواندن اطلاعات سرویس‌ها از فایل CSV
    df = pd.read_csv(csv_file, encoding="utf-8")
    if df.empty:
        await message.answer("❌ هیچ قسطی برای پرداخت یافت نشد.")
        return

    # ایجاد کیبورد inline برای نمایش قسط ها
    inline_buttons = []
    for index, row in df.iterrows():
        order_title = row['product_title']
        order_id = row['order_id']

        button_text = f"🗓️ {order_title} | سفارش: {order_id}"
        button = InlineKeyboardButton(text=button_text, callback_data=f"debts_{order_id}")
        inline_buttons.append([button])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_buttons + [[InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]]
    )
    await message.answer("سفارش خود را جهت پرداخت اقساط انتخاب کنید: ", reply_markup=keyboard)


@router.callback_query(F.data == "show_debts")
async def show_debts_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # مسیر فایل CSV مربوط به سفارش های کاربر
    user_folder = f"Data_csv/{user_id}"
    os.makedirs(user_folder, exist_ok=True)
    csv_file = os.path.join(user_folder, "installment_purchases.csv")

    # بررسی اینکه فایل CSV وجود دارد یا نه
    if not os.path.exists(csv_file):
        await callback_query.message.edit_text("❌ هیچ قسطی برای پرداخت یافت نشد.")
        return

    # خواندن اطلاعات سرویس‌ها از فایل CSV
    df = pd.read_csv(csv_file, encoding="utf-8")
    if df.empty:
        await callback_query.message.edit_text("❌ هیچ قسطی برای پرداخت یافت نشد.")
        return

    # ایجاد کیبورد inline برای نمایش قسط ها
    inline_buttons = []
    for index, row in df.iterrows():
        order_title = row['product_title']
        order_id = row['order_id']

        button_text = f"🗓️ {order_title} | سفارش: {order_id}"
        button = InlineKeyboardButton(text=button_text, callback_data=f"debts_{order_id}")
        inline_buttons.append([button])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_buttons + [[InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]]
    )
    await callback_query.message.edit_text("سفارش خود را جهت پرداخت اقساط انتخاب کنید: ", reply_markup=keyboard)



@router.callback_query(lambda c: c.data.startswith('debts_'))
async def show_service_file(callback_query: types.CallbackQuery, state: FSMContext):
    order_id = callback_query.data[len('debts_'):]
    user_id = callback_query.from_user.id
    user_folder = f"Data_csv/{user_id}"
    csv_file = os.path.join(user_folder, "installment_purchases.csv")

    if not os.path.exists(csv_file):
        await callback_query.answer(
            "❌ هیچ سفارشی برای شما یافت نشد.",
            show_alert=True
        )
        return

    df = pd.read_csv(csv_file, encoding="utf-8", dtype={"order_id": str})

    service_data = df[df["order_id"] == str(order_id)]

    if not service_data.empty:
        row = service_data.iloc[0]

        product_title = row["product_title"]
        price = int(row["price"])
        prepaid = int(row["prepaid"])
        fee = int(row["fee"])
        first_payment = int(row["first_payment"])
        unit = int(row["unit"])
        every_debt = int(row["every_debt"])
        installment_dates = row["installment_dates"]

        installment_dates_split = installment_dates.split("\n")
        inline_buttons = []
        for i in installment_dates_split:
            button_text = f"{i}"
            button = InlineKeyboardButton(text=button_text, callback_data=f"pay_debt_{i}")
            if "قسط" in i:
                inline_buttons.append([button])


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=inline_buttons + [
                [InlineKeyboardButton(text="🔙 بازگشت به لیست سفارش ها", callback_data="show_debts")],
                [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
            ]
        )

        await callback_query.message.edit_text(
            f"🧾 شماره سفارش: <code>{order_id}</code>\n\n"
            f"🎮 محصول خریداری شده:\n{product_title}\n\n"
            f"💰 قیمت محصول در زمان خرید: {price:,} تومان\n"
            f"\u200F━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 پیش‌پرداخت: {prepaid:,} تومان\n"
            f"📊 کارمزد پیش‌پرداخت: {fee:,} تومان\n\n"
            f"💳 جمع اولین مبلغ پرداخت شده: {first_payment:,} تومان\n"
            f"\u200F━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 تعداد اقساط: {unit} قسط\n"
            f"💸 مبلغ هر قسط: {every_debt:,} تومان\n"
            f"\u200F━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 برای پرداخت هرکدام از اقساط زیر آن را لمس کنید:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    else:
        await callback_query.answer(
            f"❌ سفارش {order_id} برای شما پیدا نشد.",
            show_alert=True
        )
        return
    await state.update_data(order_id=order_id, installment_dates_split=installment_dates_split, every_debt=every_debt,
                            product_title=product_title)
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('pay_debt_'))
async def show_service_file(callback_query: types.CallbackQuery, state: FSMContext):
    debt = callback_query.data[len('pay_debt_'):]
    debt_number = debt.split(":")[0].replace("💳", "").strip()
    debt_date = debt.split(":")[1].strip()

    # تبدیل تاریخ شمسی به میلادی
    year, month, day = map(int, debt_date.split("/"))
    due_date = jdatetime.date(year, month, day).togregorian()

    # محاسبه اختلاف با امروز
    days_difference = (due_date - date.today()).days




    if "پرداخت نشده" not in debt:
        await callback_query.answer("💰 این قسط قبلا پرداخت شده است.", show_alert=True)
        return


    user_data = await state.get_data()
    every_debt = user_data.get("every_debt")
    order_id = user_data.get("order_id")

    if days_difference > 20:
        await callback_query.answer(f"⏳ {days_difference} روز تا موعد قسط باقی مانده است.\n"
                                    "✅ به دلیل پرداخت قسط زودتر از موعد سررسید؛ قسط شما شامل کارمزد نمیشود.",
                                    show_alert=True)
        fee = 0

    else:
        fee = int(every_debt * 0.06)

    final_debt_price = every_debt + fee
    final_debt_price = int(final_debt_price // 1000) * 1000

    fine_ticket = None
    if days_difference == 0:
        await callback_query.answer("✅ موعد پرداخت قسط امروز است.\n"
                                    "از خوش حسابی شما سپاس گزاریم!",
                                    show_alert=True)

    elif 0 > days_difference >= -3:
        await callback_query.answer(f"⚠️ {abs(days_difference)} روز از موعد قسط گذشته است.\n"
                                    f"✅ با توجه به قوانین این قسط شامل جریمه نمیشود.",
                                    show_alert=True)

    elif -3 > days_difference >= -10:
        fine_price = 30000
        fine_ticket = fine_price * abs(days_difference)
        final_debt_price += fine_ticket

        await callback_query.answer(f"⚠️ {abs(days_difference)} روز از موعد قسط گذشته است.\n"
                                    f"⚠️ با توجه به قوانین٬\n"
                                    f"جریمه ی روزانه {fine_price:,} تومان بوده\n"
                                    f"و این قسط شامل {fine_ticket:,} تومان جریمه میشود.",
                                    show_alert=True)
    elif days_difference < -10:
        await callback_query.answer(
            f"📢❌ اکانت شما به دلیل عدم پرداخت قسط در موعد مقرر باطل شد!\n"
            f"❌ شماره سفارش: {order_id}\n",
            show_alert=True
        )
        return



    # مسیر فایل CSV شماره کارت‌ها
    cards_folder = "./Cards"
    card_file_path = os.path.join(cards_folder, "cards.csv")

    if os.path.exists(card_file_path):
        df = pd.read_csv(card_file_path)
        card_info = df[['card_number', 'name', 'count']]

        card_number = None
        name = None

        # پیدا کردن اولین کارت دارای ظرفیت
        for index, row in card_info.iterrows():
            if row["count"] < 190:
                card_number = row['card_number']
                name = row['name']
                await state.update_data(card_number=card_number)
                break

        # اگر هیچ کارتی ظرفیت نداشت
        if card_number is None:
            second_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
                ]
            )

            await callback_query.edit_text("ظرفیت کارت به کارت پر شده است،"
                                           " لطفا از طریق پشتیبانی اقدام کنید.",
                                           reply_markup=second_keyboard)
            await state.clear()
            return

    else:
        await callback_query.edit_text("❌ فایل اطلاعات کارت‌ها یافت نشد. لطفاً با پشتیبانی تماس بگیرید.")
        await state.clear()
        return


    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ارسال عکس واریزی", callback_data="payـdebt")],
        [InlineKeyboardButton(text="🔙 بازگشت به لیست سفارش ها", callback_data="show_debts")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ])

    total = f"💵 مبلغ قسط + کارمزد + جریمه = {final_debt_price:,} تومان\n" if fine_ticket else \
        f"💵 مبلغ قسط + کارمزد = {final_debt_price:,} تومان\n"
    price_details = f"💰 مبلغ قسط: {every_debt:,} تومان\n" \
                    f"💳 کارمزد: {fee:,} تومان\n" \
                    f"💳 جریمه: {fine_ticket:,} تومان\n\n" if fine_ticket else \
                    f"💰 مبلغ قسط: {every_debt:,} تومان\n" \
                    f"💳 کارمزد: {fee:,} تومان\n\n"

    await callback_query.message.edit_text(
        f"⚠️ شما در حال پرداخت {debt_number} سفارش شماره ی {order_id} هستید.\n\n"
        f"{price_details}"
        f"{total}"
        f"\u200F━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 لطفا مبلغ: <code>{int(final_debt_price * 10):,}</code> ریال به شماره کارت زیر واریز کنید."
        "\n\n"
        f"💳 شماره کارت: <code>{card_number}</code>\n"
        f"👤 صاحب حساب:\n{name}\n"
        f"\u200F━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧾 بعد از انجام عملیات، رسید واریز را از طریق گزینه زیر ارسال کنید.",
        parse_mode="HTML",
        reply_markup=keyboard
    )


    await callback_query.answer()
    await state.update_data(debt=debt, every_debt=every_debt, fee=fee, final_debt_price=final_debt_price)



@router.callback_query(F.data == "payـdebt")
async def enter_amount(callback_query: types.CallbackQuery, state: FSMContext):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
        ]
    )
    await callback_query.message.edit_text("💵 لطفاً عکس رسید انتقال را ارسال کنید.", reply_markup=keyboard)
    await state.set_state(Change.waiting_for_debt_photo)  # وضعیت برای دریافت مبلغ


@router.message(Change.waiting_for_debt_photo)
async def get_photo(message: types.Message, state: FSMContext, bot: Bot):

    user_data = await state.get_data()
    order_id = user_data.get("order_id")
    debt = user_data.get("debt")
    every_debt = user_data.get("every_debt")
    final_debt_price = user_data.get("final_debt_price")
    product_title = user_data.get("product_title")


    user_id = message.from_user.id
    username = message.from_user.username
    username_text = (
        f"@{username}"
        if username
        else f"<a href='tg://user?id={user_id}'>{user_id}</a>"
    )


    # دریافت تصویر از پیام کاربر
    if message.text:
        await message.answer("⛔ لطفا فقط تصویر رسید انتقال را بدون متن ارسال کنید!")
        await state.set_state(Change.waiting_for_debt_photo)  # وضعیت برای دریافت مبلغ
        return

    transfer_photo = message.photo[-1].file_id
    transfer_photo_id = message.message_id

    # کاربر
    await message.answer("✅ رسید شما دریافت شد.\n"
                         "تا زمان تایید پشتیبانی صبور باشید.\n"
                         f"🔢 شماره سفارش:\n"
                         f"<code>{order_id}</code>\n\n",
                         parse_mode="HTML"
                         )

    # پشتیبانی
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید", callback_data="confirm_transfer_debt")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
        ]
    )
    await bot.send_photo(
        chat_id=-1004463809616,
        photo=transfer_photo,
        caption=(
            f"👤 کاربر: <code>\n{user_id}</code>\n"
            f"🔹 یوزرنیم: \n{username_text}\n"
            f"🔢 شماره سفارش: <code>\n{order_id}</code>\n"
            f"🎮 محصول: \n{product_title}\n\n"
            f"مشخصات قسط: {debt}\n\n"
            f"💰 مبلغ هر قسط: \n{every_debt:,} تومان\n\n"
            f"💸 مبلغ واریزی: \n{final_debt_price:,} تومان\n\n"
            f"🧾 لطفاً رسید را بررسی کنید.\n"
            f"🆔 شناسه رسید: {transfer_photo_id}"
        ),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.clear()


@router.callback_query(F.data == "confirm_transfer_debt")
async def confirm_buy(callback_query: types.CallbackQuery, bot: Bot):

    caption = callback_query.message.caption.replace(
        "🧾 لطفاً رسید را بررسی کنید.",
        "✅ تایید شده."
    ).replace(
        "پرداخت نشده",
        "پرداخت شده"
    )

    user_match = re.search(r"👤 کاربر:\s*(\d+)", caption)
    order_match = re.search(r"🔢 شماره سفارش:\s*(\d+)", caption)
    photo_id_match = re.search(r"🆔 شناسه رسید:\s*(\d+)", caption)
    debt_match = re.search(r"مشخصات قسط:\s*💳?\s*قسط\s*(\d+):\s*(\d{4}/\d{2}/\d{2})", caption)

    if not user_match or not order_match or not photo_id_match or not debt_match:
        await callback_query.answer(
            "❌ استخراج اطلاعات از کپشن ناموفق بود.",
            show_alert=True
        )
        return

    user_id = user_match.group(1)
    order_id = order_match.group(1)
    transfer_photo_id = photo_id_match.group(1)
    debt_number = debt_match.group(1)
    debt_date = debt_match.group(2)


    await callback_query.message.edit_caption(
        caption=caption,
        reply_markup=None,
        parse_mode="HTML"
    )

    await bot.send_message(
        chat_id=int(user_id),
        reply_to_message_id=transfer_photo_id,
        text=(
            "✅ تراکنش شما تایید شد.\n\n"
            "🔢 شماره سفارش:\n"
            f"<code>{order_id}</code>\n\n"
            f"🧾 قسط شماره ی {debt_number} سفارش بالا با موفقیت پرداخت شد. "
        ),
        parse_mode="HTML"
    )

    await done_pay_debt(order_id, user_id, debt_date)


async def done_pay_debt(order_id, user_id, debt_date):

    user_folder = f"Data_csv/{user_id}"
    os.makedirs(user_folder, exist_ok=True)

    csv_user_file = os.path.join(user_folder, f"{user_id}.csv")
    df = pd.read_csv(csv_user_file, encoding="utf-8")
    debts = int(df['debts'].iloc[0])
    new_debts_counting = debts - 1
    df['debts'] = new_debts_counting
    # ذخیره موجودی جدید کیف پول
    # df['wallet'] = new_wallet_balance
    # ذخیره تغییرات
    df.to_csv(csv_user_file, index=False, encoding="utf-8")

    csv_file = os.path.join(user_folder, "installment_purchases.csv")
    df = pd.read_csv(csv_file, encoding="utf-8", dtype={"order_id": str})

    order_data = df[df["order_id"] == str(order_id)]

    if not order_data.empty:
        index = order_data.index[0]
        row = order_data.iloc[0]

        installment_dates = row["installment_dates"]

        installment_dates_split = installment_dates.split("\n")
        installment_details = ""

        for i in installment_dates_split:
            if debt_date in i and "پرداخت نشده" in i:
                installment_details += i.replace("پرداخت نشده", "پرداخت شده")
            else:
                installment_details += i

            installment_details += "\n"

        installment_details = installment_details.rstrip("\n")

        df.at[index, "installment_dates"] = installment_details

        df.to_csv(csv_file, index=False, encoding="utf-8")

        return True

    return False



@router.callback_query(lambda c: c.data.startswith('confirm_delete_'))
async def confirm_delete_service(callback_query: types.CallbackQuery):
    service_name = callback_query.data[len('confirm_delete_'):]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ بله، حذف کن", callback_data=f"delete_{service_name}")],
            [InlineKeyboardButton(text="🔙 خیر", callback_data=f"service_{service_name}")],
        ]
    )
    await callback_query.message.edit_text(
        f"⚠️ آیا از حذف سرویس '{service_name}' اطمینان دارید؟",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('delete_'))
async def delete_service(callback_query: types.CallbackQuery):
    service_name = callback_query.data[len('delete_'):]
    user_id = callback_query.from_user.id
    csv_file = os.path.join(f"Data_csv/{user_id}", "intallment_purchases.csv")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به لیست سرویس‌ها", callback_data=f"show_debts")],
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
