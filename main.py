import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN
import sqlite3
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import logging


bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

#id (INTEGER, PRIMARY KEY, AUTOINCREMENT) name (TEXT) age (INTEGER) grade (TEXT)

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
	CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
    grade TEXT NOT NULL)
	''')
    conn.commit()
    conn.close()

init_db()

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("/start - Бот уточнит данные студента и сохранит информацию в базе данных.")
    await message.answer("/list - Бот выведет инфо о студентах их базы данных.")

@dp.message(Command("list"))
async def list_users(message: Message):
    try:
        conn = sqlite3.connect('school_data.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name, age, grade FROM users")
        users = cur.fetchall()
        conn.close()

        if not users:
            await message.answer("База данных пуста.")
            return

        response = "Список студентов:\n"
        for user in users:
            response += f"ID: {user[0]}, Имя: {user[1]}, Возраст: {user[2]}, Класс: {user[3]}\n"

        await message.answer(response)
    except Exception as e:
        logging.error(f"Ошибка при получении данных: {e}")
        await message.answer("Произошла ошибка при извлечении данных из базы.")



@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Введите имя студента:")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите возраст студента:")
    await state.set_state(Form.age)

# name (TEXT) age (INTEGER) grade (TEXT)
@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите класс студента:")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state:FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()
    await message.answer("Данные сохранены в базе данных.")

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO users (name, age, grade) VALUES (?, ?, ?)''',(user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()

    await state.clear()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())