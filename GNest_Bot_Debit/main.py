try:
    import os
    import sys
    import time
    import asyncio
    import logging
    import threading
    from dotenv import load_dotenv
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext
    from aiogram.client.session.aiohttp import AiohttpSession
except ImportError:
    from module_installer import Module_installer
finally:
    import os
    import sys
    import time
    import asyncio
    import logging
    import threading
    from dotenv import load_dotenv
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext
    from aiogram.client.session.aiohttp import AiohttpSession



from handlers import start, wallet, mydebts, law, contact_support, guide, referral, \
    store, manual_wallet, to_csv, sending_msg, user_info, checking_services


# بارگذاری توکن رباط
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN_DEBIT")

if not TOKEN:
    raise ValueError("❌ توکن پیدا نشد!")

# تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot_logs.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
dp = Dispatcher(storage=MemoryStorage())


# لاگ هندلر برای ارسال به تلگرام
class TelegramLogHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.send_log(log_entry))

    async def send_log(self, log_entry):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=log_entry[:4000])
        except Exception as e:
            print(f"Failed to send log to Telegram: {e}")


async def main():
    PROXY = "socks5://127.0.0.1:10808"
    session = AiohttpSession(proxy=PROXY)



    bot = Bot(
        token=TOKEN,
        session=session
    )




    dp.include_routers(start.router, store.router, mydebts.router, law.router, contact_support.router, wallet.router,
                       guide.router, manual_wallet.router, to_csv.router, sending_msg.router,
                       user_info.router, referral.router)


    # اضافه کردن هندلر لاگ برای ارسال به تلگرام
    telegram_handler = TelegramLogHandler(bot, chat_id=-1002554791670)
    telegram_handler.setLevel(logging.INFO)
    telegram_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(telegram_handler)


    logger.info("Starting...")
    await checking_services.on_start(bot)
    await dp.start_polling(bot)





# @dp.message()
# async def get_chat_id(message: Message):
#     print("CHAT ID:", message.chat.id)
#     print("CHAT TYPE:", message.chat.type)
#     print("CHAT TITLE:", message.chat.title)


    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
