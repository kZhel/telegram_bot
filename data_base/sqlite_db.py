import sqlite3 as sq
from create_bot import bot

def sql_start():
    global base,cur
    base=sq.connect('daily_tracker.db')
    cur=base.cursor()
    if base:
        print('База данных подключена')
    base.execute('CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY AUTOINCREMENT,userid TEXT,name TEXT, details TEXT, status INTEGER)')
    base.execute('CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY AUTOINCREMENT,userid TEXT,name TEXT, details TEXT, datetime TEXT)')
    base.commit()

async def sql_add_habit_command(tuple2):
    cur.execute('insert into habits(userid,name,details,status) values (?,?,?,?)',tuple2)
    base.commit()

async def sql_add_plan_command(tuple3):
    cur.execute('insert into plans(userid,name,details,datetime) values (?,?,?,?)',tuple3)
    base.commit()

async def sql_read_command(message):
    await bot.send_message(message.from_user.id,'Твои привычки:')
    for ret in cur.execute(f'select name, details, status from habits where userid={message.from_user.id} order by status').fetchall():
        if ret[2]:
            stat='Выполнено'
        else:
            stat='Не выполнено'
        await bot.send_message(message.from_user.id, f'{ret[0]}\nДетали: {ret[1]}\nСтатус: {stat}')
    await bot.send_message(message.from_user.id,'Твои планы:')
    for ret in cur.execute(f'select name, details, datetime from plans where userid={message.from_user.id} order by datetime').fetchall():
        await bot.send_message(message.from_user.id, f'{ret[0]}\nДетали: {ret[1]}\nВремя: {ret[2]}')

async def sql_read_habits_to_delete(message):
    return cur.execute(f'select id, name, details from habits where userid={message.from_user.id}').fetchall()

async def sql_read_plans_to_delete(message):
    return cur.execute(f'select id, name, details,datetime from plans where userid={message.from_user.id}').fetchall()

async def sql_delete_habit(data):
    cur.execute(f'Delete from habits where id={data}')
    base.commit()

async def sql_delete_plan(data):
    cur.execute(f'Delete from plans where id={data}')
    base.commit()

async def sql_read_habits_to_check(id):
    return cur.execute(f'select id, name, details from habits where userid={id} and status=0').fetchall()

async def sql_read_plans_to_check(id):
    return cur.execute(f'select id, name, details, datetime from plans where userid={id}').fetchall()

async def sql_check_habit(data):
    cur.execute(f'update habits set status=1 where id={data}')
    base.commit()

async def sql_check_if_notify():
    return cur.execute('select userid, id, name, details, datetime from plans').fetchall()

async def sql_done_habits():
    cur.execute('update habits set status=0 where status=1')
    base.commit()

async def sql_read_users():
    return cur.execute('select distinct userid from habits where status=0').fetchall()