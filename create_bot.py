from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN='5518040390:AAH3zlx8QKKdQH2Z1RCRMalX9BavaJNbJ3E'

storage=MemoryStorage()

bot=Bot(token=TOKEN)
dp=Dispatcher(bot, storage=storage)