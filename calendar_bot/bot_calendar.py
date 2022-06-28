import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery


calendar_callback = CallbackData('dialog_calendar', 'act', 'year', 'month', 'day','hour','minute')

class Calendar:
    months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июнь", "Июль", "Авг", "Сен", "Окт", "Ноя", "Дек"]

    def __init__(self, year: int = datetime.now().year, month: int = datetime.now().month,
    hour: int=datetime.now().hour, minute: int=datetime.now().minute):
        self.year = year
        self.month = month
        self.hour=hour
        self.minute=minute

    async def start_calendar(self, year: int = datetime.now().year) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=5)
        # first row - years
        inline_kb.row()
        for value in range(year, year + 5):
            inline_kb.insert(InlineKeyboardButton(
                value,
                callback_data=calendar_callback.new("SET-YEAR", value, -1, -1, -1, -1)
            ))
        # nav buttons
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            '<-',
            callback_data=calendar_callback.new("PREV-YEARS", year, -1, -1, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '->',
            callback_data=calendar_callback.new("NEXT-YEARS", year, -1, -1, -1, -1)
        ))

        return inline_kb

    async def _get_month_kb(self, year: int):
        inline_kb = InlineKeyboardMarkup(row_width=6)
        # first row with year button
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            year,
            callback_data=calendar_callback.new("START", year, -1, -1, -1, -1)
        ))
        # two rows with 6 months buttons
        inline_kb.row()
        for month in self.months[0:6]:
            inline_kb.insert(InlineKeyboardButton(
                month,
                callback_data=calendar_callback.new("SET-MONTH", year, self.months.index(month) + 1, -1, -1, -1)
            ))
        inline_kb.row()
        for month in self.months[6:12]:
            inline_kb.insert(InlineKeyboardButton(
                month,
                callback_data=calendar_callback.new("SET-MONTH", year, self.months.index(month) + 1, -1, -1, -1)
            ))
        return inline_kb

    async def _get_days_kb(self, year: int, month: int):
        inline_kb = InlineKeyboardMarkup(row_width=7)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            year,
            callback_data=calendar_callback.new("START", year, -1, -1, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            self.months[month - 1],
            callback_data=calendar_callback.new("SET-YEAR", year, -1, -1, -1, -1)
        ))
        
        if month in [1,3,5,7,8,10,12]:
            inline_kb.row()
            day=1
            while day<32:
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("SET-DAY", year, month, day, -1, -1)))
                day+=1
        elif month==2:
            if year%4==0 and year%100!=0:
                inline_kb.row()
                day=1
                while day<30:
                    inline_kb.insert(InlineKeyboardButton(
                        str(day), callback_data=calendar_callback.new("SET-DAY", year, month, day, -1, -1)))
                    day+=1
            else:
                inline_kb.row()
                day=1
                while day<29:
                    inline_kb.insert(InlineKeyboardButton(
                        str(day), callback_data=calendar_callback.new("SET-DAY", year, month, day, -1, -1)))
                    day+=1
        elif month in [4,6,9,11]:
            inline_kb.row()
            day=1
            while day<31:
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("SET-DAY", year, month, day, -1, -1)))
                day+=1
        return inline_kb

    async def _get_hours_kb(self, year: int, month: int, day: int):
        inline_kb = InlineKeyboardMarkup(row_width=6)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            year,
            callback_data=calendar_callback.new("START", year, -1, -1, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            self.months[month - 1],
            callback_data=calendar_callback.new("SET-YEAR", year, -1, -1, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            day,
            callback_data=calendar_callback.new("SET-MONTH", year, month, -1, -1, -1)
        ))

        inline_kb.row()
        hour=0
        while hour<24:
            inline_kb.insert(InlineKeyboardButton(
                str(hour), callback_data=calendar_callback.new("SET-HOUR", year, month, day, hour, -1)))
            hour+=1
        
        return inline_kb

    async def _get_minutes_kb(self, year: int, month: int, day: int, hour: int):
        inline_kb = InlineKeyboardMarkup(row_width=7)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            year,
            callback_data=calendar_callback.new("START", year, -1, -1, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            self.months[month - 1],
            callback_data=calendar_callback.new("SET-YEAR", year, -1, -1, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            day,
            callback_data=calendar_callback.new("SET-MONTH", year, month, -1, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            hour,
            callback_data=calendar_callback.new("SET-DAY", year, month, day, -1, -1)
        ))

        inline_kb.row()
        minutes=0
        while minutes<60:
            inline_kb.insert(InlineKeyboardButton(
                str(minutes), callback_data=calendar_callback.new("SET-MINUTE", year, month, day, hour, minutes)))
            minutes+=1
        
        return inline_kb

    async def process_selection(self, query: CallbackQuery, data: CallbackData) -> tuple:
        return_data = (False, None)
        if data['act'] == "SET-YEAR":
            await query.message.edit_reply_markup(await self._get_month_kb(int(data['year'])))
        if data['act'] == "PREV-YEARS":
            new_year = int(data['year']) - 5
            await query.message.edit_reply_markup(await self.start_calendar(new_year))
        if data['act'] == "NEXT-YEARS":
            new_year = int(data['year']) + 5
            await query.message.edit_reply_markup(await self.start_calendar(new_year))
        if data['act'] == "START":
            await query.message.edit_reply_markup(await self.start_calendar(int(data['year'])))
        if data['act'] == "SET-MONTH":
            await query.message.edit_reply_markup(await self._get_days_kb(int(data['year']), int(data['month'])))
        if data['act'] == "SET-DAY":
            await query.message.edit_reply_markup(await self._get_hours_kb(int(data['year']), int(data['month']), int(data['day'])))
        if data['act'] == "SET-HOUR":
            await query.message.edit_reply_markup(await self._get_minutes_kb(int(data['year']), int(data['month']), int(data['day']), 
            int(data['hour'])))
        if data['act'] == "SET-MINUTE":
            temp_date=datetime(int(data['year']), int(data['month']), int(data['day']), int(data['hour']), int(data['minute']))
            if temp_date<datetime.now():
                await query.message.answer("Выбранная дата уже прошла, выбери другую дату")
                await query.message.edit_reply_markup(await self.start_calendar())
            else:
                await query.message.delete_reply_markup()  
                return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']), int(data['hour']), int(data['minute']))
        return return_data