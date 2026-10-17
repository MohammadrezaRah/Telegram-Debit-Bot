from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
import os
import pandas as pd

from handlers import start



router = Router()


@router.message(F.text == "📜 قوانین")
async def laws(message: types.Message):
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="پذیرفتن قوانین ✅")],
        ],
        resize_keyboard=True
    )
    ID = message.chat.id
    directory = f"Data_csv/{ID}"
    file_path = os.path.join(directory, f"{ID}.csv")
    mssg = (
        "🎖 قوانین خرید اقساطی مجموعه گیم نست:\n\n"

        "🔹 ۱. پس از تأیید و ثبت پیش‌پرداخت، محصول خریداری‌شده در اختیار خریدار قرار خواهد گرفت. "
        "خریدار موظف است نحوه استفاده از محصول را مطابق قوانین و شرایط درج‌شده "
        "در صفحه قوانین وب‌سایت مجموعه رعایت نماید. "
        "قوانین مربوط به نحوه استفاده از محصول از طریق این صفحه game-nest.ir/rules قابل مشاهده می‌باشد.\n\n"
                
        "🔸 ۲. مبلغ باقی‌مانده پس از اولین پرداخت، بنا به انتخاب خریدار، "
        "قابل تسویه در ۱ الی ۳ قسط می‌باشد. "
        "تعداد اقساط در زمان ثبت خرید مشخص شده و مبنای پرداخت و تسویه قرار خواهد گرفت.\n\n"

        "🔹 ۳. بابت هر پرداخت، کارمزدی معادل ۶٪ از مبلغ همان تراکنش محاسبه و به مبلغ قابل پرداخت اضافه خواهد شد."
        "این کارمزد مستقل از مبلغ اصل بدهی بوده و پرداخت آن بر عهده خریدار می‌باشد.\n\n"

        "🔸 ۵. اولین قسط، ۳۰ روز پس از تاریخ پرداخت و تأیید پیش‌پرداخت سررسید خواهد شد. "
        "سررسید هر یک از اقساط بعدی نیز به ترتیب، ۳۰ روز پس از سررسید قسط قبلی خواهد بود. "
        "تاریخ سررسید اقساط در زمان ثبت خرید تعیین و به خریدار اعلام می‌گردد و "
        "خریدار موظف است پرداخت هر قسط را در موعد مقرر انجام دهد.\n\n"

        "🔻 ۶. هر قسط از تاریخ سررسید، حداکثر تا ۳ روز بدون اعمال جریمه قابل پرداخت خواهد بود. "
        "در صورت پرداخت قسط در این بازه، استفاده از ظرفیت اکانت بدون محدودیت ادامه خواهد داشت. "
        "پس از گذشت مهلت ۳ روزه، قسط وارد وضعیت تأخیر در پرداخت خواهد شد. "
        "چنانچه پرداخت هر قسط به مدت بیشتر از ۱۰ روز از تاریخ سررسید به تأخیر بیفتد، "
        "حق امتیاز خریدار نسبت به محصول خریداری‌شده سلب خواهد شد. "
        "در این شرایط، تمامی مبالغی که خریدار تا آن زمان پرداخت کرده است، "
        "به عنوان خسارت ناشی از عدم ایفای تعهدات مالی محسوب شده و قابل استرداد نخواهد بود؛ "
        "همچنین پس از گذشت ۱۰ روز تاخیر از تاریخ سررسید٬ قرارداد منقسخ خواهد شد.\n\n"
        
        "🔻 ۷. در صورت تأخیر بیش از سه روز در پرداخت قسط از تاریخ سررسید، بابت هر روز تأخیر از تاریخ سررسید٬\n"
        "مبلغ ۳۰ هزار تومان جریمه دریافت خواهد شد.\n\n"
       
        "🔹 ۸. پس از پرداخت پیش‌پرداخت، محصول خریداری‌شده در اختیار خریدار قرار می‌گیرد "
        "و خریدار تا زمان تسویه کامل تمامی اقساط، صرفا حق استفاده از محصول خریداری‌شده را خواهد داشت. "
        "پس از پرداخت و تسویه کامل تمامی مبالغ ذکر شده، "
        "محصول خریداری‌شده متعلق به خریدار خواهد بود."
    )
    # بررسی فایل و خواندن محتوا با pandas
    try:
        df = pd.read_csv(file_path)

        if "law" not in df.columns or df["law"].isnull().all():
            # اگر ستون "law" وجود ندارد یا تمام مقادیر آن null هستند
            await message.answer(mssg, reply_markup=reply_keyboard)
        elif str(df["law"].iloc[0]).lower() != "true":
            # اگر تمام مقادیر ستون "law" برابر با False است
            await message.answer(mssg, reply_markup=reply_keyboard)
        else:
            # اگر قوانین قبلاً قبول شده‌اند
            await message.answer(mssg)
            await message.answer("شما از قبل قوانین را قبول کرده‌اید!")


    except FileNotFoundError:
        # اگر فایل وجود ندارد
        await message.answer("فایل پیدا نشد. لطفاً از گزینه /start استفاده کنید.")


@router.message(F.text == "پذیرفتن قوانین ✅")
async def accept(message: types.Message, state: FSMContext):
    ID = message.chat.id
    directory = f"Data_csv/{ID}"
    file_path = os.path.join(directory, f"{ID}.csv")
    # بررسی اینکه فایل وجود دارد یا نه
    if not os.path.exists(file_path):
        await message.answer("⛔ فایل قوانین شما پیدا نشد. لطفاً از گزینه /start استفاده کنید.")
        return
    df = pd.read_csv(file_path)
    if "law" not in df.columns:
        df["law"] = False
    df["law"] = True
    df.to_csv(file_path, index=False)

    await message.answer("قوانین پذیرفته شد!")

    await start.back_to_main_text(message, state)
