from create_bot import dp, bot
from aiogram import types
from data_base import sqlite_db
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery
from calendar_bot import calendar_callback, Calendar
from keyboards import kboard

import asyncio
temp_id=None

async def send_notify():
    notif=await sqlite_db.sql_check_if_notify()
    datenow=datetime.now()
    for noty in notif:
        if datenow.strftime("%d/%m/%Y %H:%M")==noty[4]:
            global temp_id
            temp_id=noty[1]
            await bot.send_message(noty[0],f'Пришло время выполнить план:\n{noty[2]}\nДетали: {noty[3]}', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(f'Отметить выполнение', callback_data=f'checkPlans {noty[1]},{noty[2]}')).\
            add(InlineKeyboardButton(f'Отменить план', callback_data=f'delPlan {noty[1]},{noty[2]}')))

async def unset_daily_progress():
    datenow=datetime.now()
    if datenow.strftime("%H:%M")=="00:00":
        await sqlite_db.sql_done_habits()

async def send_check_notify():
    datenow=datetime.now()
    if datenow.strftime("%H:%M")=="19:00":
        users= await sqlite_db.sql_read_users()
        for user in users:
            await bot.send_message(user[0], 'Не забудь отметить, что ты сделал сегодня')
            read=await sqlite_db.sql_read_habits_to_check(user[0])
            await bot.send_message(user[0],'Выбери то, что ты выполнил сегодня:')
            for ret in read:
                await bot.send_message(user[0], text=f'{ret[1]}\nДетали: {ret[2]}', reply_markup=InlineKeyboardMarkup().\
                    add(InlineKeyboardButton(f'Отметить выполнение', callback_data=f'checkHabit {ret[0]},{ret[1]}')))
    
async def cor_task():
    while True:
        await send_notify()
        await unset_daily_progress()
        await send_check_notify()
        await asyncio.sleep(60)
        
   