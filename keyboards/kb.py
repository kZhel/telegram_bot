from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1=KeyboardButton('Добавить план')
b2=KeyboardButton('Добавить привычку')
b3=KeyboardButton('Удалить план')
b4=KeyboardButton('Удалить привычку')
b5=KeyboardButton('Посмотреть список')
b6=KeyboardButton('Отметить выполнение')
b7=KeyboardButton('Подробнее о командах')

kboard=ReplyKeyboardMarkup(resize_keyboard=True)

kboard.row(b1,b3).row(b2,b4).add(b5).add(b6).add(b7)