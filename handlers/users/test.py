import filters
import mysql.connector
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.builtin import CommandStart, Text
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import datetime

from keyboards.default.menu_btns import admin_btn, menu_btn
from loader import dp

from data.config import ADMINS

# MySQL configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'test'


# MySQL connection function
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def users_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users")
    users = cursor.fetchall()
    return [user[0] for user in users]


def is_contractors(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE telegram_id = %s", (user_id,))
    user = cursor.fetchone()
    return user[0] if user else None


def in_list(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (user_id,))
    user = cursor.fetchone()
    return user


def add_admin(user_id, full_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'admin')",
                   (user_id, full_name))
    conn.commit()


def add_contractor(contractor_id, full_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'contractor')",
                   (contractor_id, full_name))
    conn.commit()


@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    if in_list(user_id=user_id) and str(is_contractors(user_id=user_id)) == 'contractor':
        await message.reply("Assalomu alaykum! Siz shartnomachi bo'lsangiz, savdoning miqdorini kiritishingiz mumkin.")
    else:
        if in_list(user_id=user_id) and str(is_contractors(user_id=user_id)) == 'admin':
            await message.reply("Admin menyusiga muvaffaqiyatli kirdingiz.", reply_markup=admin_btn())
        elif int(user_id) == int(ADMINS[0]):
            add_admin(user_id=user_id, full_name=full_name)
            await message.reply("Admin hisobiga muvaffaqiyatli ro'yxatdan o'tdingiz.", reply_markup=admin_btn())
        else:
            await message.reply("Sizning botdan foydalanishingiz cheklangan. Admin bilan bog'laning.")


@dp.message_handler(Text(equals="Menyuga qaytish"))
async def back_to_home(message: types.Message):
    await message.answer("Admin menyu", reply_markup=admin_btn())


# Add contractor (Admin only)
@dp.message_handler(Text(equals="Shartnomachi qo'shish"))
async def handle_add_contractor(message: types.Message):
    if int(message.from_user.id) != int(ADMINS[0]):
        return await message.reply("Siz admin emassiz.")
    await message.reply("Shartnomachi ID va ismini kiriting:\n\nNamuna: \n123456789 John Smith", reply_markup=menu_btn())


# Delete contractor
@dp.message_handler(Text(equals="Shartnomachini o'chirish"))
async def handle_delete_contractor(message: types.Message):
    if int(message.from_user.id) != int(ADMINS[0]):
        return await message.reply("Siz admin emassiz.")
    await message.reply("Shartnomachi ID sini kiriting:", reply_markup=menu_btn())


@dp.message_handler()
async def delete_contractor(message: types.Message):
    contractor_id = message.text.split(" ")[0]
    if contractor_id.isdigit():
        if in_list(contractor_id):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE telegram_id = %s", (contractor_id,))
            conn.commit()
            await message.reply(f"Shartnomachi ID [ {contractor_id} ] muvaffaqiyatli o'chirildi!")
            cursor.close()
        else:
            await message.reply(f"[ {contractor_id} ] shartnomachi mavjud emas!")
    else:
        await message.reply("Shartnomachi ID sini kiriting!")


# Handling the contractor's sales input
@dp.message_handler()
async def handle_save_sales(message: types.Message):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
    user = cursor.fetchone()
    if user and str(user[4]) == 'contractor':
        if message.text.isdigit():
            sales_value = float(message.text)
            cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
            user_id = cursor.fetchone()[0]

            # Insert sale record
            today = datetime.date.today()
            cursor.execute("INSERT INTO daily_sales (user_id, sales, date) VALUES (%s, %s, %s)", (user_id, sales_value, today))
            connection.commit()

            # Calculate total sales
            cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
            total_sales = cursor.fetchone()[0]

            cursor.execute("SELECT target FROM users WHERE id = %s", (user_id,))
            target = cursor.fetchone()[0]

            percent = (total_sales / target) * 100
            cursor.execute("INSERT INTO monthly_reports (user_id, month, year, total_sales, percent) VALUES (%s, %s, "
                           "%s, %s, %s)",
                           (user_id, today.month, today.year, total_sales, percent))
            connection.commit()

            await message.reply(f"Savdo qo'shildi: {sales_value}$.\nJami savdo: {total_sales}$.\nReja: {percent:.2f}% "
                                f"bajarildi.")
            cursor.close()
            connection.close()
        else:
            await message.reply("Savdoni faqat raqamlarda kiriting!")
    else:
        await message.answer("Siz shartnomachi emassiz!")
