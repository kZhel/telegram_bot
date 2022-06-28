from aiogram.utils import executor
from create_bot import dp
from data_base import sqlite_db
from notifies import bot_notify_sender
import asyncio

async def on_startup(_):
    print('Бот вышел в онлайн')
    sqlite_db.sql_start()
    asyncio.create_task(bot_notify_sender.cor_task())

from handlers import main_handlers

main_handlers.register_handlers(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)