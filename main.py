import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN

loop = asyncio.get_event_loop()

storage = MemoryStorage()

bot = Bot(BOT_TOKEN, parse_mode='HTML')

dp = Dispatcher(bot, storage=storage, loop=loop)

if __name__ == '__main__':
    from handlers import dp, send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)