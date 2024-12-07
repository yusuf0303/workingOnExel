import filters
import mysql.connector
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.builtin import CommandStart
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import datetime

from loader import dp

from data.config import ADMINS

# MySQL konfiguratsiyasi
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'test'


# MySQL bilan bog'lanish
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# Admin uchun menyu
admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(KeyboardButton('Shartnomachi qo\'shish'), KeyboardButton('Shartnomachini o\'chirish'))
admin_keyboard.add(KeyboardButton('Hisobotlar'))

# Foydalanuvchi uchun menyu
contractor_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
contractor_keyboard.add(KeyboardButton('Pul kiritish'), KeyboardButton('O\'tgan oy hisobotlari'))
contractor_keyboard.add(KeyboardButton('Barcha hisobotlar'))


menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(KeyboardButton('Menyuga qaytish'))


# /start komandasi handleri
@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    # Foydalanuvchi ro'yxatda bormi?
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
    user = cursor.fetchone()

    if user and int(user[1]) != int(ADMINS[0]):
        await message.reply("Assalomu alaykum! Siz shartnomachi bo'lsangiz, savdoning miqdorini kiritishingiz mumkin.",
                            reply_markup=contractor_keyboard)
    else:
        # Yangi foydalanuvchi admin bo'lsa
        if user and int(user[1]) == int(ADMINS[0]):
            await message.reply("Admin menyusiga muvaffaqiyatli kirdingiz.", reply_markup=admin_keyboard)
        elif int(message.from_user.id) == int(ADMINS[0]):  # Admin ID bilan almashtirish
            cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'admin')",
                           (message.from_user.id, message.from_user.full_name))
            connection.commit()
            await message.reply("Admin hisobiga muvaffaqiyatli ro'yxatdan o'tdingiz.", reply_markup=admin_keyboard)
        else:
            await message.reply("Sizning botdan foydalanishingiz cheklangan. Admin bilan bog'laning.")

    cursor.close()
    connection.close()


@dp.message_handler(lambda message: message.text == "Menyuga qaytish")
async def back_to_home(message: types.Message):
    await message.answer("Admin menyu", reply_markup=admin_keyboard)


# Shartnomachi qo'shish (Admin uchun)
@dp.message_handler(lambda message: message.text == "Shartnomachi qo'shish")
async def add_contractor(message: types.Message):
    # Admin bo'lishi kerak
    if int(message.from_user.id) != int(ADMINS[0]):  # Admin ID bilan almashtirish
        return await message.reply("Siz admin emassiz.")

    await message.reply("Shartnomachi ID va ismini kiriting:\n\nNamuna: \n123456789 John Smith",
                        reply_markup=menu_keyboard)


@dp.message_handler(lambda message: message.text == "Shartnomachini o'chirish")
async def add_contractor(message: types.Message):
    # Admin bo'lishi kerak
    if int(message.from_user.id) != int(ADMINS[0]):  # Admin ID bilan almashtirish
        return await message.reply("Siz admin emassiz.")

    await message.reply("Shartnomachi ID sini kiriting:",
                        reply_markup=menu_keyboard)


@dp.message_handler(lambda message: message.text == "Hisobotlar")
async def add_contractor(message: types.Message):
    # Admin bo'lishi kerak
    if int(message.from_user.id) != int(ADMINS[0]):  # Admin ID bilan almashtirish
        return await message.reply("Siz admin emassiz.")

    await message.reply("Jami hisobotlar",
                        reply_markup=menu_keyboard)


# Shartnomachi ism kiritilganda uni qo'shish
@dp.message_handler(lambda message: message.text != "Shartnomachi qo'shish")
async def add_contractor_name(message: types.Message):
    if int(message.from_user.id) == int(ADMINS[0]):
        split_text = message.text.split(' ')
        if split_text[0].isdigit():
            contractor_id = message.text.split(' ')[0]
            if len(split_text) >= 3:
                contractor_name = split_text[1] + ' ' + ' ' + split_text[2]
                connection = get_db_connection()
                cursor = connection.cursor()

                cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'contractor')",
                               (contractor_id, contractor_name))
                connection.commit()

                await message.reply(
                    f"{contractor_name} [ {contractor_id} ] shartnomachi sifatida muvaffaqiyatli qo'shildi.",
                    reply_markup=admin_keyboard)

                cursor.close()
                connection.close()
            elif len(split_text) == 2:
                contractor_name = split_text[1]
                connection = get_db_connection()
                cursor = connection.cursor()

                cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'contractor')",
                               (contractor_id, contractor_name))
                connection.commit()

                await message.reply(
                    f"{contractor_name} [ {contractor_id} ] shartnomachi sifatida muvaffaqiyatli qo'shildi.",
                    reply_markup=admin_keyboard)

                cursor.close()
                connection.close()
            else:
                await message.reply("Shartnomachi ma'lumotlari to'liq emas yoki xato!")
        else:
            await message.reply("Shartnomachi ma'lumotlari to'liq emas yoki xato!")


# Savdo qo'shish (Shartnomachi uchun)
@dp.message_handler(lambda message: message.text == "Pul kiritish")
async def enter_sales(message: types.Message):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
    user = cursor.fetchone()
    print(user, user[4])
    if user and user[4] == 'contractor':
        await message.reply("Savdo miqdorini kiriting:")


# Savdo miqdorini kiritganda uni qo'shish
@dp.message_handler(lambda message: message.text.isdigit())
async def save_sales(message: types.Message):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
    user = cursor.fetchone()
    if user and user[4] == 'contractor':
        sales_value = float(message.text)
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
        user_id = cursor.fetchone()[0]

        # Savdo qo'shish
        today = datetime.date.today()
        cursor.execute("INSERT INTO daily_sales (user_id, sales, date) VALUES (%s, %s, %s)", (user_id, sales_value, today))
        connection.commit()

        # Jami savdolarni hisoblash
        cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
        total_sales = cursor.fetchone()[0]

        # Maqsadni olish (limit 78000$)
        cursor.execute("SELECT target FROM users WHERE id = %s", (user_id,))
        target = cursor.fetchone()[0]

        percent = (total_sales / target) * 100
        cursor.execute(
            "INSERT INTO monthly_reports (user_id, month, year, total_sales, percent) VALUES (%s, %s, %s, %s, %s)",
            (user_id, today.month, today.year, total_sales, percent))
        connection.commit()

        await message.reply(
            f"Savdo qo'shildi: {sales_value}$.\nJami savdo: {total_sales}$.\nReja: {percent:.2f}% bajarildi.")

        cursor.close()
        connection.close()

