from aiogram import Dispatcher, types
from create_bot import dp,bot
from keyboards import kboard
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery
from calendar_bot import calendar_callback, Calendar
from data_base import sqlite_db

class FSMHabit(StatesGroup):
    name=State()
    details=State()

class FSMPlans(StatesGroup):
    name=State()
    details=State()

plan_tuple=None

# Предоставление клавиатуры для выбора действия
async def start_command(message: types.Message):
    await message.answer("Привет, я помогу тебе отслеживать выполнение твоих ежедневных привычек и планов. Давай начнем!")
    await none_command(message)

# Добавление новой привычки
async def new_habit(message: types.Message):
    await FSMHabit.name.set()
    await message.reply('Напиши название новой привычки', reply_markup=ReplyKeyboardRemove())
    await message.answer('Если передумал нажми отмена', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(text='отмена', callback_data='отмена')))

async def load_habit_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name']=message.text
    await FSMHabit.next()
    await message.reply("Теперь напиши дополнительные детали, если их нет напиши 'нет'")
    await message.answer('Если передумал нажми отмена', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(text='отмена', callback_data='отмена')))

async def load_habit_details(message: types.Message, state: FSMContext):
    Id=message.from_user.id
    async with state.proxy() as data:
        data['details']=message.text
        tuple1=tuple(data.values())
    tuple2=(Id,*tuple1,0)
    await sqlite_db.sql_add_habit_command(tuple2)
    await message.answer("Новая привычка добавлена",reply_markup=kboard)
    await state.finish()

# Добавление нового плана
async def new_plan(message: types.Message):
    await FSMPlans.name.set()
    await message.reply('Напиши название нового плана', reply_markup=ReplyKeyboardRemove())
    await message.answer('Если передумал нажми отмена', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(text='отмена', callback_data='отмена')))
 
async def load_plan_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name']=message.text
    await FSMPlans.next()
    await message.reply("Теперь напиши дополнительные детали, если их нет напиши 'нет'")
    await message.answer('Если передумал нажми отмена', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(text='отмена', callback_data='отмена')))

async def load_plan_details(message: types.Message, state: FSMContext):
    Id=message.from_user.id
    async with state.proxy() as data:
        data['details']=message.text
        tuple1=tuple(data.values())
    global plan_tuple
    plan_tuple=(Id,*tuple1)
    await state.finish()
    await simple_cal_handler(message)

async def simple_cal_handler(message: types.Message):
    await message.answer("Теперь выбери время, когда нужно напомнить о твоих планах: ", reply_markup=await Calendar().start_calendar())
    await message.answer('Если передумал нажми отмена', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(text='отмена', callback_data='отмена_календарь')))

@dp.callback_query_handler(calendar_callback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await Calendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Ты выбрал время {date.strftime("%d/%m/%Y %H:%M")}'
        )
        
        tuple3=(*plan_tuple,date.strftime("%d/%m/%Y %H:%M"))
        await sqlite_db.sql_add_plan_command(tuple3)
        await callback_query.message.answer("Новый план добавлен",reply_markup=kboard)

# Прерывание добавления новой цели
async def cancel_command(message: types.Message, state: FSMContext):
    cur_state=await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    await message.reply("OK",reply_markup=kboard)

@dp.callback_query_handler(text='отмена',state='*')
async def cancel_button(callback: types.CallbackQuery, state:FSMContext):
    cur_state=await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    await callback.message.reply("OK",reply_markup=kboard)

@dp.callback_query_handler(text='отмена_календарь')
async def cancel_button(callback: types.CallbackQuery):
    await callback.message.reply("OK",reply_markup=kboard)

# Удаление привычки
async def delete_habit(message: types.Message):
    read=await sqlite_db.sql_read_habits_to_delete(message)
    await bot.send_message(message.from_user.id,'Выбери привычку, которую хочешь удалить:', reply_markup=kboard)
    for ret in read:
        await bot.send_message(message.from_user.id, text=f'{ret[1]}\nДетали: {ret[2]}', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(f'Удалить', callback_data=f'delHabit {ret[0]},{ret[1]}')))

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('delHabit '))
async def del_habit_callback(callback_query: types.CallbackQuery):
    tempdata=callback_query.data.replace('delHabit ','').split(',')
    await sqlite_db.sql_delete_habit(tempdata[0])
    await callback_query.answer(text=f'Привычка {tempdata[1]} удалена', show_alert=True)

# Удаление плана
async def delete_plan(message: types.Message):
    read=await sqlite_db.sql_read_plans_to_delete(message)
    await bot.send_message(message.from_user.id,'Выбери план, который хочешь удалить:', reply_markup=kboard)
    for ret in read:
        await bot.send_message(message.from_user.id, text=f'{ret[1]}\nДетали: {ret[2]}\nВремя: {ret[3]}', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(f'Удалить', callback_data=f'delPlan {ret[0]},{ret[1]}')))  

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('delPlan '))
async def del_plan_callback(callback_query: types.CallbackQuery):
    tempdata=callback_query.data.replace('delPlan ','').split(',')
    await sqlite_db.sql_delete_plan(tempdata[0])
    await callback_query.answer(text=f'План {tempdata[1]} удален', show_alert=True)

# Контроль выполнения
async def check_habit(message: types.Message):
    id=message.from_user.id
    read=await sqlite_db.sql_read_habits_to_check(id)
    await bot.send_message(message.from_user.id,'Выбери то, что ты выполнил сегодня:', reply_markup=kboard)
    for ret in read:
        await bot.send_message(message.from_user.id, text=f'{ret[1]}\nДетали: {ret[2]}', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(f'Отметить выполнение', callback_data=f'checkHabit {ret[0]},{ret[1]}')))
    read2=await sqlite_db.sql_read_plans_to_check(id)
    for ret in read2:
        await bot.send_message(message.from_user.id, text=f'{ret[1]}\nДетали: {ret[2]}\nВремя: {ret[3]}', reply_markup=InlineKeyboardMarkup().\
            add(InlineKeyboardButton(f'Отметить выполнение', callback_data=f'checkPlans {ret[0]},{ret[1]}')))

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('checkHabit '))
async def check_habit_callback(callback_query: types.CallbackQuery):
    tempdata=callback_query.data.replace('checkHabit ','').split(',')
    await sqlite_db.sql_check_habit(tempdata[0])
    await callback_query.answer(text=f'Привычка {tempdata[1]} выполнена', show_alert=True)

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('checkPlans '))
async def check_plans_callback(callback_query: types.CallbackQuery):
    tempdata=callback_query.data.replace('checkPlans ','').split(',')
    await sqlite_db.sql_delete_plan(tempdata[0])
    await callback_query.answer(text=f'План {tempdata[1]} выполнен и удален', show_alert=True)

# Просмотр всех целей
async def all_goals(message: types.Message):
    await sqlite_db.sql_read_command(message)
    await none_command(message)

async def help_command(message: types.Message):
    await message.answer("*Команды:* \n\
        _Добавить план_-добавление нового плана и установка времени, когда нужно о нем напомнить\n\
        _Добавить привычку_-добавление привычки, выполнение которой отслеживается ежедневно\n\
        _Удалить план_-вывод всех твоих плнаов и возможность удалить ненужные\n\
        _Удалить привычку_-вывод всех твоих привычек и возможность удалить ненужные\n\
        _Посмотреть список_-вывод списка всех твоих привычек с их статусом на сегодняшний день\n\
        _Отметить выполнение_-вывод всех твоих невыполненных сегодня привычек и предстоящих планов",parse_mode="Markdown")
    await none_command(message)

# Предоставление клавиатуры для выбора действия
async def none_command(message : types.Message):
    await message.answer("Выбери нужную команду из предложенных",reply_markup=kboard)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel_command, state="*", commands='отмена')
    dp.register_message_handler(cancel_command, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(start_command,commands=['start'])
    dp.register_message_handler(new_habit, text="Добавить привычку", state=None)
    dp.register_message_handler(load_habit_name, state=FSMHabit.name)
    dp.register_message_handler(load_habit_details, state=FSMHabit.details)
    dp.register_message_handler(new_plan, text="Добавить план", state=None)
    dp.register_message_handler(load_plan_name, state=FSMPlans.name)
    dp.register_message_handler(load_plan_details, state=FSMPlans.details)
    dp.register_message_handler(delete_habit, text="Удалить привычку")
    dp.register_message_handler(delete_plan, text="Удалить план")
    dp.register_message_handler(all_goals, text="Посмотреть список")
    dp.register_message_handler(check_habit, text="Отметить выполнение")
    dp.register_message_handler(help_command, text="Подробнее о командах")
    dp.register_message_handler(help_command,commands=['help'])
    dp.register_message_handler(none_command)