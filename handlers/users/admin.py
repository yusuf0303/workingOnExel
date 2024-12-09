import mysql.connector
from data.config import ADMINS
from loader import dp
from aiogram import types
from keyboards.default.menu_btns import admin_btn


# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="test"
    )


def in_list(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (user_id,))
    user = cursor.fetchone()
    return user


def is_contractors(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT role FROM users WHERE telegram_id = %s", (user_id,))
    user = cursor.fetchone()
    return user[0] if user else None


def add_admin(user_id, full_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'admin')",
                   (user_id, full_name))
    conn.commit()


@dp.message_handler(commands=['admin'])
async def admin_menu(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.reply("Admin menyusiga muvaffaqiyatli kirdingiz.", reply_markup=admin_btn())
    else:
        await message.reply("Siz admin emassiz.")


@dp.message_handler(commands='reports')
async def send_reports(message: types.Message):
    user_id = message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    # Foydalanuvchi roli (admin yoki boshqa) ni olish
    cursor.execute("SELECT role FROM users WHERE telegram_id = %s", (user_id,))
    user_role = cursor.fetchone()

    if user_role and user_role[0] == "admin":  # Faqat adminlar uchun
        # Barcha shartnomachilarning jami savdolarini olish
        cursor.execute("""
            SELECT u.name, u.telegram_id, u.role,
                   SUM(ds.sales) AS total_sales, 
                   m.month, m.year, 
                   m.percent
            FROM users u
            LEFT JOIN daily_sales ds ON u.id = ds.user_id
            LEFT JOIN monthly_reports m ON u.id = m.user_id 
            GROUP BY u.id, m.month, m.year
            ORDER BY m.year DESC, m.month DESC;
        """)
        reports = cursor.fetchall()

        if reports:
            report_text = "Barcha shartnomachilarning jami savdolari:\n\n"

            for report in reports:
                name, telegram_id, role, total_sales, month, year, percent = report

                if str(role) != "admin":
                    # Formatlashni faqat total_sales mavjud bo'lsa amalga oshiradi
                    if total_sales is not None:
                        total_sales_text = f"{total_sales:.2f}$"
                    else:
                        total_sales_text = "Savdo ma'lumotlari mavjud emas"
                    if percent is not None:
                        percent_text = f"{percent:.2f}%"
                    else:
                        percent_text = "Reja bajarilmagan"

                    report_text += f"Shartnomachi: {name}\n"
                    report_text += f"Telegram ID: {telegram_id}\n"
                    report_text += f"Hisobot: {month}/{year}\n"
                    report_text += f"Jami savdo: {total_sales_text}\n"  # Bu yerda formatlash shartli bo'ladi
                    report_text += f"Reja bajarilgan: {percent_text}\n\n"

            await message.reply(report_text)
        else:
            await message.reply("Hisobotlar topilmadi.")

        cursor.close()
        conn.close()
    else:
        await message.reply("Siz admin emassiz.")
