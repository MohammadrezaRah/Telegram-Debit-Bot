import json
import os
import re
import random
import pandas as pd
from datetime import datetime, timedelta
import jdatetime
from aiogram import types, Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


router = Router()


class Change(StatesGroup):
    waiting_for_prepaid_amount = State()
    waiting_for_debts_unit = State()
    waiting_for_vendor_id = State()
    waiting_for_photo = State()
#############################################
#############################################
vendor_price = 0.05                         #
#############################################
#############################################


@router.message(F.text == "فروشنده ها")
async def store_command(message: Message, state: FSMContext):


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )
    await message.answer("لطفا آیدی عددی کاربر را وارد کنید:", reply_markup=keyboard)
    await state.set_state(Change.waiting_for_vendor_id)


@router.message(Change.waiting_for_vendor_id)
async def get_service_name_ovpn(message: types.Message, state: FSMContext):

    vendor_id = message.text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 اضافه کردن", callback_data="vendor_add")],
            [InlineKeyboardButton(text="🔙 حذف کردن", callback_data="vendor_delete")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
        ]
    )
    await message.answer("آیدی دریافت شد! لطفا حرکت بعدی را انتخاب کنید:", reply_markup=keyboard)
    await state.update_data(vendor_id=vendor_id)


@router.callback_query(F.data.in_(["vendor_add", "vendor_delete"]))
async def manage_vendor(callback_query: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    vendor_id = data.get("vendor_id")

    file_path = "vendors.txt"

    if callback_query.data == "vendor_add":
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{vendor_id}\n")

        await callback_query.message.edit_text("✅ فروشنده با موفقیت اضافه شد.")

    elif callback_query.data == "vendor_delete":
        if not os.path.exists(file_path):
            await callback_query.message.answer("❌ فایل وندورها وجود ندارد.")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(file_path, "w", encoding="utf-8") as f:
            for line in lines:
                if line.strip() != str(vendor_id):
                    f.write(line)

        await callback_query.message.edit_text("🗑 فروشنده حذف شد.")

    await state.clear()


@router.message(F.text == "✅ باز کردن فروش")
async def store_command(message: Message):

    sales_file = "sales.txt"

    with open(sales_file, "w", encoding="utf-8") as f:
        f.write("yes")

    await message.answer(
        "✅ فروش باز شد.\n\n"
    )


@router.message(F.text == "⛔ بستن فروش")
async def store_command(message: Message):

    sales_file = "sales.txt"

    with open(sales_file, "w", encoding="utf-8") as f:
        f.write("no")

    await message.answer(
        "⛔ فروش بسته شد.\n\n"
    )




@router.message(F.text == "🛒 خرید")
async def store_command(message: Message):

    sales_file = "sales.txt"

    # اگر فایل نبود، پیش‌فرض باز در نظر بگیر
    if os.path.exists(sales_file):
        with open(sales_file, "r", encoding="utf-8") as f:
            status = f.read().strip().lower()

        if status == "no":
            await message.answer(
                "⛔ فروش اقساط در حال حاضر بسته است.\n\n"
                "📢 زمان باز شدن فروش در کانال اعلام خواهد شد.\n\n"
                "✅ برای خرید نقدی با پشتیبانی ما در ارتباط باشید.\n\n"
                "@Game_Nest_Admin"
            )
            return


    ID = message.chat.id
    directory = f"Data_csv/{ID}"
    user_path = os.path.join(directory, f"{ID}.csv")
    # بررسی اینکه فایل وجود دارد یا نه
    if not os.path.exists(user_path):
        await message.answer("⛔ فایل شما پیدا نشد. لطفاً از گزینه /start استفاده کنید.")
        return

    df = pd.read_csv(user_path)
    if "law" not in df.columns:
        df["law"] = False
        df.to_csv(user_path, index=False)  # ذخیره تغییرات در فایل

    if str(df["law"].iloc[0]).lower() != "true":
        reply_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="پذیرفتن قوانین ✅")],
                [KeyboardButton(text="📜 قوانین")],
            ],
            resize_keyboard=True
        )
        await message.answer(
            "✅ لطفا قبل از خرید قوانین را مطالعه کنید! "
            "خرید شما به منزله ی قبول قوانین تلقی خواهد شد.",
            reply_markup=reply_keyboard
        )
        return

    keyboard = make_product_keyboard()

    await message.answer(
        "شما وارد بخش فروشگاه شدید.\n"
        "🎮 لطفاً یکی از محصولات را انتخاب کنید:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "🛒 خرید")
async def show_menu(callback_query: types.CallbackQuery):

    sales_file = "sales.txt"

    # اگر فایل نبود، پیش‌فرض باز در نظر بگیر
    if os.path.exists(sales_file):
        with open(sales_file, "r", encoding="utf-8") as f:
            status = f.read().strip().lower()

        if status == "no":
            await callback_query.message.answer(
                "⛔ فروش اقساط در حال حاضر بسته است.\n\n"
                "📢 زمان باز شدن فروش در کانال اعلام خواهد شد.\n\n"
                "✅ برای خرید نقدی با پشتیبانی ما در ارتباط باشید.\n\n"
                "@Game_Nest_Admin"
            )
            return


    ID = callback_query.from_user.id
    directory = f"Data_csv/{ID}"
    user_path = os.path.join(directory, f"{ID}.csv")
    # بررسی اینکه فایل وجود دارد یا نه
    if not os.path.exists(user_path):
        await callback_query.message.edit_text("⛔ فایل شما پیدا نشد. لطفاً از گزینه /start استفاده کنید.")
        return

    df = pd.read_csv(user_path)
    if "law" not in df.columns:
        df["law"] = False
        df.to_csv(user_path, index=False)  # ذخیره تغییرات در فایل

    if df["law"].eq(False).all():
        reply_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="پذیرفتن قوانین ✅")],
                [KeyboardButton(text="📜 قوانین")],
            ],
            resize_keyboard=True
        )
        await callback_query.message.answer(
            "✅ لطفا قبل از خرید قوانین را مطالعه کنید! "
            "خرید شما به منزله ی قبول قوانین تلقی خواهد شد.",
            reply_markup=reply_keyboard
        )
        return

    keyboard = make_product_keyboard()

    msg = "شما وارد بخش فروشگاه شدید.\n🎮 لطفاً یکی از محصولات را انتخاب کنید:"

    try:
        await callback_query.message.edit_text(
        msg,
            reply_markup=keyboard
        )
    except Exception:
        await callback_query.message.answer(
            "شما وارد بخش فروشگاه شدید.\n"
            "🎮 لطفاً یکی از محصولات را انتخاب کنید:",
            reply_markup=keyboard
        )


def make_product_keyboard():
    global products


    base_dir = "../GNest_Products_Bot/list"

    products = []

    # =========================
    # دریافت محصولات
    # =========================

    for product_id in os.listdir(base_dir):

        product_dir = os.path.join(
            base_dir,
            product_id
        )

        if not os.path.isdir(product_dir):
            continue

        product_path = os.path.join(
            product_dir,
            "product.json"
        )

        if not os.path.exists(product_path):
            continue

        with open(
                product_path,
                "r",
                encoding="utf-8"
        ) as f:

            product = json.load(f)

        products.append({
            "data": product,
            "path": product_path
        })

    # =========================
    # ساخت کیبورد
    # =========================

    keyboard_buttons = []

    for product in products:
        product_data = product["data"]
        title = product_data["title"]
        price = product_data["price"]

        if "پلاس" in title:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{title} | قیمت: {price:,} تومان ",
                    callback_data=f"product_{product_data['id']}"
                )
            ])

    # دکمه بازگشت
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🔙 بازگشت به منوی اصلی",
            callback_data="back_to_main"
        )
    ])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=keyboard_buttons
    )
    return keyboard


@router.callback_query(F.data.startswith("product_"))
async def new_products_query(callback_query: types.CallbackQuery, state: FSMContext):

    product_id = int(callback_query.data.split("_", 1)[1])

    price = 0
    title = ""
    product_data = ""
    try:
        for i in products:
            product_data = i["data"]

            if product_id == product_data["id"]:
                price = product_data["price"]
                title = product_data["title"]
                break

    except NameError:
        await callback_query.message.delete()
        await show_menu(callback_query)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تایید و ادامه", callback_data="go_for_debts")],
        [InlineKeyboardButton(text="🔙 بازگشت به لیست محصولات", callback_data="🛒 خرید")]
    ])

    await callback_query.message.edit_text(
        "🔹 مشخصات محصول انتخاب شده:\n\n"
        f"{product_info(product_data)}",
        reply_markup=keyboard
    )

    await state.update_data(
        product_title=title,
        product_id=product_id,
        price=price
    )


def product_info(product):

    product_caption = (
        f"🎮 {product['title']}\n\n"
        f"💰 قیمت: {product['price']:,} تومان\n\n"
    )

    if product["description"]:
        product_caption += (
            f"⚠️ {product['description']}\n\n"
        )

    # =========================
    # ویژگی‌ها
    # =========================

    if product.get("features"):

        product_caption += "\n"

        for key, value in product["features"].items():
            product_caption += (
                f"🔹 {key}: {value}\n"
            )

        product_caption += "\n"

    # =========================
    # گزینه‌ها
    # =========================

    if product.get("options"):

        valid_options = [
            op
            for op in product["options"]
            if op.get("title") != "primary"
        ]

        if valid_options:

            product_caption += (
                "🎯 گزینه‌های موجود:\n"
            )

            for op in valid_options:
                product_caption += (
                    f"🔸 {op['title']}\n"
                )

            product_caption += "\n"

    # =========================
    # ادامه Caption
    # =========================

    product_caption += (
        f"{product['url']}\n\n"
    )

    return product_caption


######################################################################################
@router.callback_query(F.data == "go_for_debts")
async def new_products_query(callback_query: types.CallbackQuery, state: FSMContext):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به لیست محصولات", callback_data="🛒 خرید")]
    ])

    with open("vendors.txt", "r", encoding="utf-8") as f:
        vendors = f.read().splitlines()

    user_data = await state.get_data()
    price = user_data.get("price")
    pre_price = (price // 3) + 1000
    pre_price = int(pre_price // 1000) * 1000


    if str(callback_query.from_user.id) in vendors:
        price = price * vendor_price

    await callback_query.message.edit_text(
        "📦 لطفا مبلغ پیش پرداخت را به تومان مشخص کنید:\n\n"
        f"⚠️ حداقل مبلغ واریز نقدی این سفارش شما باید\n"
        f" بیشتر از "
        f"<code>{pre_price:,}</code>"
        f" تومان"
        f"\n و کمتر از <code>{price:,}</code> تومان باشد.\n\n"
        # f"<code>{pre_price:,}</code>\n"
        f"برای انتخاب حداقل روی /{pre_price} بزنید.",
        reply_markup=keyboard, parse_mode="HTML"
    )

    await state.update_data(
        price=int(price), pre_price=pre_price)
    await state.set_state(Change.waiting_for_prepaid_amount)


@router.message(Change.waiting_for_prepaid_amount)
async def new_products_query(message: types.Message, state: FSMContext):

    user_data = await state.get_data()
    price = user_data.get("price")
    pre_price = user_data.get("pre_price")

    text = message.text

    try:
        prepaid = int(text.replace(",", "").replace(".", "").replace("/", ""))
        if prepaid < pre_price or prepaid > price:
            raise NameError

    except ValueError:
        await message.answer("⚠️ لطفاً فقط عدد وارد کنید!")
        await state.set_state(Change.waiting_for_prepaid_amount)
        return
    except NameError:
        await message.answer(f"⚠️ مبلغ پیش پرداخت باید بیشتر از {pre_price:,} تومان و کمتر از  {price:,} تومان باشد! ")
        await state.set_state(Change.waiting_for_prepaid_amount)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به لیست محصولات", callback_data="🛒 خرید")]
    ])

    await message.answer(
        "✅ مبلغ دریافت شد\n\n"
        "🔹 لطفا در ادامه تعداد اقساط مورد نظر خود را به صورت عدد وارد کنید.\n\n"
        "شما میتوانید حداقل ۱ قسط و حداکثر ۳ قسط انتخاب کنید.\n"
        "\n\n/1"
        "\n\n/2"
        "\n\n/3",
        reply_markup=keyboard, parse_mode="HTML"
    )

    await state.update_data(
        prepaid=prepaid)
    await state.set_state(Change.waiting_for_debts_unit)



@router.message(Change.waiting_for_debts_unit)
async def new_products_query(message: types.Message, state: FSMContext, bot: Bot):

    user_data = await state.get_data()
    product_title = user_data.get("product_title")
    product_id = user_data.get("product_id")
    price = user_data.get("price")
    prepaid = user_data.get("prepaid")
    fee = prepaid * 0.06 + 1001
    fee = (fee // 1000) * 1000
    total_payment = int(fee + prepaid)


    text = message.text

    try:
        unit = int(text.replace("/", ""))
        if 1 > unit or 3 < unit:
            raise NameError
    except ValueError:
        await message.answer("⚠️ لطفاً فقط عدد وارد کنید!")
        await state.set_state(Change.waiting_for_debts_unit)
        return
    except NameError:
        await message.answer("⚠️ توجه کنید؛ تعداد اقساط باید بین ٬۱ ۲ یا ۳ ماه باشد!")
        await state.set_state(Change.waiting_for_debts_unit)
        return



    start_date = datetime.now()

    installment_text = ""

    for i in range(1, unit + 1):
        due_date = start_date + timedelta(days=30 * i)
        jalali_date = jdatetime.datetime.fromgregorian(datetime=due_date)

        installment_text += (
            f"💳 قسط {i}: "
            f"{jalali_date.strftime('%Y/%m/%d')}:پرداخت نشده\n"
        )

    # خواندن موجودی کیف پول از فایل CSV
    user_id = message.from_user.id

    csv_file = f"Data_csv/{user_id}/{user_id}.csv"

    if not os.path.exists(csv_file):
        await message.answer(
            "⛔ فایل شما پیدا نشد. لطفاً از گزینه /start استفاده کنید."
        )
        return

    df = pd.read_csv(csv_file, encoding="utf-8")
    wallet_balance = int(df["wallet"].iloc[0])

    # مبلغی که از کیف پول قابل پرداخت است
    wallet_payment = min(total_payment, wallet_balance)
    new_wallet_balance = int(wallet_balance - wallet_payment)

    # مبلغ باقی‌مانده پس از استفاده از کیف پول
    remaining_payment = int(max(total_payment - wallet_balance, 0))

    every_debt = (price - prepaid) // unit

    # شماره سفارش
    order_number_path = "./order_number.txt"
    if not os.path.exists(order_number_path):
        order_id = random.randint(100000, 999999)
        with open(order_number_path, "w", encoding="utf-8") as f:
            f.write(str(order_id))

    else:
        with open(order_number_path, "r", encoding="utf-8") as f:
            old_number = int(f.read().strip())

        order_id = random.randint(old_number + 1, old_number + 30)
        with open(order_number_path, "w", encoding="utf-8") as f:
            f.write(str(order_id))

    await message.answer(
        f"🛒 اطلاعات خرید شما:\n\n"
        f"🔢 شماره سفارش:\n<code>{order_id}</code>\n\n"
        f"🆔 شناسه محصول:\n<code>{product_id}</code>\n\n"
        f"🎮 محصول:\n{product_title}\n\n"
        f"💰 مبلغ کل:\n{price:,} تومان\n\n"
        f"💵 مبلغ پیش‌پرداخت:\n{prepaid:,} تومان\n\n"
        f"💳 کارمزد پرداخت قسطی:\n{fee:,.0f} تومان\n\n"
        f"💰 جمع کل اولین پرداخت:\n{total_payment:,.0f} تومان\n\n"
        f"💳 موجودی کیف پول:\n{wallet_balance:,} تومان\n\n"
        f"💸 مبلغ قابل پرداخت پس از کسر کیف پول:\n{remaining_payment:,} تومان\n\n"
        f"📅 تعداد اقساط:\n{unit} ماه\n\n"
        f"💵 مبلغ هر قسط~\n{every_debt:,} تومان\n\n"
        f"📆 سررسید اقساط:\n"
        f"{installment_text}",
        parse_mode="HTML"
    )



    if wallet_payment != 0:
        await message.answer(
            "موجودی جدید کیف پول\n"
            f"{new_wallet_balance:,} تومان خواهد بود."
        )

    await state.update_data(user_id=user_id, order_id=order_id, remaining_payment=remaining_payment,
                            unit=unit, every_debt=every_debt, product_title=product_title, price=price,
                            total_payment=total_payment)

    new_data = {
        "full_name": message.from_user.full_name,
        "username": message.from_user.username,
        "user_id": message.from_user.id,
        "chat_id": message.chat.id,
        "order_id": order_id,
        "product_id": product_id,
        "product_title": product_title,
        "price": price,
        "prepaid": prepaid,
        "fee": fee,
        "total_payment": total_payment,
        "wallet_balance": wallet_balance,
        "new_wallet_balance": new_wallet_balance,
        "first_payment": remaining_payment,
        "unit": unit,
        "every_debt": every_debt,
        "installment_dates": installment_text
    }

    file_path = f"Data_csv/{user_id}/orders/{order_id}.txt"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(new_data, file, ensure_ascii=False, indent=4)

    if remaining_payment < 100000:

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ])
        await message.answer(
            "⚠️ لطفا از متن بالا اسکرین شات بگیرید یا آن را در جایی ذخیره کنید.\n\n"
            f"✅ خرید شما با موفقیت انجام شد.\n\n"
            f"در ادامه لطفاً شماره سفارش خود را برای پشتیبانی بفرستید.\n\n"
            f"🔢 شماره سفارش:\n"
            f"<code>{order_id}</code>\n\n"
            f"💬 @Game_Nest_Admin\n\n",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        await done_pay(bot, order_id, user_id)


    else:

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

                await message.edit_text("ظرفیت کارت به کارت پر شده است،"
                                        " لطفا از طریق پشتیبانی اقدام کنید.",
                                        reply_markup=second_keyboard)
                await state.clear()
                return

        else:
            await message.edit_text("❌ فایل اطلاعات کارت‌ها یافت نشد. لطفاً با پشتیبانی تماس بگیرید.")
            await state.clear()
            return


        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ ارسال عکس واریزی", callback_data="go_pay")],
            [InlineKeyboardButton(text="🔄 شروع مجدد", callback_data="🛒 خرید")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ])
        await message.answer(
            "⚠️ از متن بالا اسکرین شات بگیرید یا آن را در جایی ذخیره کنید.\n\n"
            f"💰 لطفا مبلغ: <code>{int(remaining_payment * 10):,}</code> ریال به شماره کارت زیر واریز کنید."
            "\n\n"
            f"💳 شماره کارت: <code>{card_number}</code>\n"
            f"👤 صاحب حساب:\n{name}\n\n"
            f"🧾 بعد از انجام عملیات، رسید واریز را از طریق گزینه زیر ارسال کنید.",
            parse_mode="HTML",
            reply_markup=keyboard
        )


async def done_pay(bot: Bot, order_id, user_id):

    file_path = f"Data_csv/{user_id}/orders/{order_id}.txt"

    with open(file_path, "r", encoding="utf-8") as file:
        user_data = json.load(file)


    full_name = user_data.get("full_name")
    username = user_data.get("username")
    order_id = user_data.get("order_id")
    product_title = user_data.get("product_title")
    product_id = user_data.get("product_id")
    price = user_data.get("price")
    prepaid = user_data.get("prepaid")
    unit = user_data.get("unit")
    fee = user_data.get("fee")
    total_payment = user_data.get("total_payment")
    new_wallet_balance = user_data.get("new_wallet_balance")
    remaining_payment = user_data.get("first_payment")
    every_debt = user_data.get("every_debt")
    installment_text = user_data.get("installment_dates")

    # مسیر فایل CSV
    csv_file = f"Data_csv/{user_id}/{user_id}.csv"  # مسیر فایل CSV که برای هر کاربر ایجاد شده است
    # اگر فایل وجود ندارد، پیامی ارسال کنیم و از ادامه فرآیند جلوگیری کنیم
    if not os.path.exists(csv_file):
        await bot.send_message(user_id, "⛔ فایل شما پیدا نشد. لطفاً از گزینه /start استفاده کنید.")

    df = pd.read_csv(csv_file, encoding="utf-8")

    debts = int(df['debts'].iloc[0])
    new_debts_counting = debts + unit
    df['debts'] = new_debts_counting

    # ذخیره موجودی جدید کیف پول
    df['wallet'] = new_wallet_balance
    # ذخیره تغییرات
    df.to_csv(csv_file, index=False, encoding="utf-8")

    if "referral" in df.columns and pd.notna(df.loc[0, "referral"]):
        await referral_buy_confirm(bot, order_id, user_id)

    save_installment_purchase(
        order_id,
        user_id,
        product_id,
        product_title,
        price,
        prepaid,
        fee,
        total_payment,
        remaining_payment,
        unit,
        every_debt,
        installment_text
    )

    await bot.send_message(
        chat_id=1574768588,
        text=f"""
                👤 کاربر زیر{product_title}  خریداری نمود:

            🔹 نام:    {full_name}
            🔹 یوزرنیم:    {f"@{username}" if username else
        f"<a href='tg://user?id={user_id}'>{user_id}</a>"}
               🆔 آیدی عددی: <code>{user_id}</code>
                """,
        parse_mode="HTML"
    )


async def referral_buy_confirm(bot: Bot, order_id, user_id):

    file_path = f"Data_csv/{user_id}/orders/{order_id}.txt"

    with open(file_path, "r", encoding="utf-8") as file:
        user_data = json.load(file)

    product_title = user_data.get("product_title")
    prepaid = user_data.get("prepaid")
    full_name = user_data.get("full_name")
    username = user_data.get("username")


    # مسیر فایل CSV
    csv_file = f"Data_csv/{user_id}/{user_id}.csv"  # مسیر فایل CSV که برای هر کاربر ایجاد شده است
    # اگر فایل وجود ندارد، پیامی ارسال کنیم و از ادامه فرآیند جلوگیری کنیم
    if not os.path.exists(csv_file):
        await bot.send_message(user_id, "⛔ فایل شما پیدا نشد. لطفاً از گزینه /start استفاده کنید.")
        return

    df = pd.read_csv(csv_file, encoding="utf-8")

    referral_id = int(df.loc[0, "referral"])
    referral_user_file = f"Data_csv/{referral_id}/{referral_id}.csv"
    referral_ref_file = f"Data_csv/{referral_id}/referrals.csv"
    referral_buy_file = f"Data_csv/{referral_id}/referrals_buy.csv"

    ref_df = pd.read_csv(referral_user_file, encoding="utf-8")
    ref_ref_df = pd.read_csv(referral_ref_file, encoding="utf-8")
    ref_buy_df = pd.read_csv(referral_buy_file, encoding="utf-8")

    for i, row in ref_ref_df.iterrows():
        if row["user_id"] == user_id:
            ref_ref_df.loc[i, "buy_count"] += 1
            break

    commission = int(prepaid * 0.01)
    ref_buy_df["buy_count"] += 1
    ref_buy_df["earning"] += int(commission)

    ref_wallet = int(ref_df["wallet"].iloc[0])
    new_ref_wallet = ref_wallet + commission
    ref_df.loc[0, "wallet"] = new_ref_wallet

    ref_df.to_csv(referral_user_file, index=False, encoding="utf-8")
    ref_ref_df.to_csv(referral_ref_file, index=False, encoding="utf-8")
    ref_buy_df.to_csv(referral_buy_file, index=False, encoding="utf-8")

    await bot.send_message(
        chat_id=referral_id,
        text=f"""
                👤 کاربر زیرمجموعه ی شما{product_title} خریداری نمود:

            🔹 نام:    {full_name}
            🔹 یوزرنیم:    {f"@{username}" if username else
        f"<a href='tg://user?id={user_id}'>{user_id}</a>"}

                🪙 پورسانت شما: {int(commission):,} تومان 
                💰 موجودی جدید: {ref_df["wallet"].iloc[0]:,} تومان 
                """,
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=1574768588,
        text=f"""
                👤 کاربر زیر{product_title}  خریداری نمود:

            🔹 نام:    {full_name}
            🔹 یوزرنیم:    {f"@{username}" if username else
        f"<a href='tg://user?id={user_id}'>{user_id}</a>"}
               🆔 آیدی عددی: <code>{user_id}</code>

                زیر مجموعه ی کاربر:  
            <a href='tg://user?id={referral_id}'>{referral_id}</a>
                """,
        parse_mode="HTML"
    )


def save_installment_purchase(
        order_id,
        user_id,
        product_id,
        product_title,
        price,
        prepaid,
        fee,
        total_payment,
        remaining_payment,
        unit,
        every_debt,
        installment_text
):

    print("saving file")
    user_folder = f"Data_csv/{user_id}"
    os.makedirs(user_folder, exist_ok=True)

    csv_file = os.path.join(
        user_folder,
        "installment_purchases.csv"
    )

    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=[
            "order_id",
            "product_id",
            "product_title",
            "price",
            "prepaid",
            "fee",
            "total_payment",
            "first_payment",
            "unit",
            "every_debt",
            "installment_dates"
        ])
    else:
        df = pd.read_csv(csv_file, encoding="utf-8")

    new_data = {
        "order_id": order_id,
        "product_id": product_id,
        "product_title": product_title,
        "price": price,
        "prepaid": prepaid,
        "fee": fee,
        "total_payment": total_payment,
        "first_payment": remaining_payment,
        "unit": unit,
        "every_debt": every_debt,
        "installment_dates": installment_text
    }

    new_data_df = pd.DataFrame([new_data])

    df = pd.concat(
        [df, new_data_df],
        ignore_index=True
    )

    int_columns = [
        "order_id",
        "product_id",
        "price",
        "prepaid",
        "fee",
        "total_payment",
        "first_payment",
        "unit",
        "every_debt"
    ]

    for column in int_columns:
        df[column] = df[column].astype("Int64")

    df.to_csv(
        csv_file,
        index=False,
        encoding="utf-8"
    )

    print(
        f"اطلاعات خرید اقساطی کاربر {user_id} ذخیره شد."
    )


@router.callback_query(F.data == "go_pay")
async def enter_amount(callback_query: types.CallbackQuery, state: FSMContext):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
        ]
    )
    await callback_query.message.edit_text("💵 لطفاً عکس رسید انتقال را ارسال کنید.", reply_markup=keyboard)
    await state.set_state(Change.waiting_for_photo)  # وضعیت برای دریافت مبلغ


@router.message(Change.waiting_for_photo)
async def get_photo(message: types.Message, state: FSMContext, bot: Bot):

    user_data = await state.get_data()
    order_id = user_data.get("order_id")
    product_title = user_data.get("product_title")
    price = user_data.get("price")
    prepaid = user_data.get("prepaid")
    total_payment = user_data.get("total_payment")
    remaining_payment = user_data.get("remaining_payment")
    unit = user_data.get("unit")
    every_debt = user_data.get("every_debt")

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
        await state.set_state(Change.waiting_for_photo)  # وضعیت برای دریافت مبلغ
        return

    transfer_photo = message.photo[-1].file_id
    transfer_photo_id = message.message_id

    # کاربر
    await message.answer("✅ خرید شما با موفقیت به پایان رسید.\n"
                         f"در ادامه لطفاً شماره سفارش خود را برای پشتیبانی بفرستید.\n\n"
                         f"🔢 شماره سفارش:\n"
                         f"<code>{order_id}</code>\n\n"
                         f"💬 @Game_Nest_Admin\n\n",
                         parse_mode="HTML"
                         )

    # پشتیبانی
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید", callback_data="confirm_transfer_done")],
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
            f"💰 قیمت محصول: \n{price:,} تومان\n"
            f"💵 پیش‌پرداخت: \n{prepaid:,} تومان\n\n"
            f"💳 جمع اولین پرداخت: \n{total_payment:,} تومان\n"
            f"💸 مبلغ واریزی: \n{remaining_payment:,} تومان\n\n"
            f"📅 تعداد اقساط: \n{unit} ماه\n"
            f"💰 مبلغ هر قسط: \n{every_debt:,} تومان\n\n"
            f"🧾 لطفاً رسید را بررسی کنید.\n"
            f"🆔 شناسه رسید: {transfer_photo_id}"
        ),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.clear()


@router.callback_query(F.data == "confirm_transfer_done")
async def confirm_buy(callback_query: types.CallbackQuery, bot: Bot):

    caption = callback_query.message.caption.replace(
        "🧾 لطفاً رسید را بررسی کنید.",
        "✅ تایید شده."
    )

    user_match = re.search(r"👤 کاربر:\s*(\d+)", caption)
    order_match = re.search(r"🔢 شماره سفارش:\s*(\d+)", caption)
    photo_id_match = re.search(r"🆔 شناسه رسید:\s*(\d+)", caption)
    if not user_match or not order_match or not photo_id_match:
        await callback_query.answer(
            "❌ استخراج اطلاعات از کپشن ناموفق بود.",
            show_alert=True
        )
        return

    user_id = user_match.group(1)
    order_id = order_match.group(1)
    transfer_photo_id = photo_id_match.group(1)


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
            "💬 @Game_Nest_Admin"
        ),
        parse_mode="HTML"
    )

    await done_pay(bot, order_id, user_id)



async def get_and_remove_line_csv(file_path: str):
    if os.path.exists(file_path):
        # خواندن فایل CSV
        df = pd.read_csv(file_path, encoding="utf-8")
        before = len(df)

        if not df.empty:
            # دریافت اولین سطر از فایل
            first_row = df.iloc[0]
            # حذف اولین سطر از دیتافریم
            df = df.drop(index=0)
            # بازنویسی فایل CSV با دیتافریم جدید
            df.to_csv(file_path, index=False, encoding="utf-8")
            # تبدیل سطر استخراج شده به یک دیکشنری یا هر چیزی که لازم دارید
            line = first_row["link"]
            username = first_row["username"]
            password = first_row["password"]

            return line, username, password, len(df), before  # سطر استخراج شده را به صورت دیکشنری باز می‌گرداند
        else:
            return False, False, False, len(df), before   # اگر فایل CSV خالی باشد
    else:
        return False, False, False, False, False  # اگر فایل وجود نداشته باشد

