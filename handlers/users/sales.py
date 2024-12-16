import mysql.connector
from aiogram import types
from loader import dp, bot
import datetime
from handlers.users.admin import in_list


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sales_bot" 
    )


@dp.message_handler()
async def handle_save_sales(message: types.Message):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Foydalanuvchi ma'lumotlarini olish
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
    user = cursor.fetchone()

    # Foydalanuvchi shartnomachi bo'lsa
    if user and user[3] == 'contractor':
        # Faqat raqamlarni qabul qilish
        if message.text.isdigit() or isinstance(float(message.text), float):
            sales_value = float(message.text)

            # Foydalanuvchi ID'sini olish
            cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
            user_id = cursor.fetchone()[0]

            today = datetime.date.today()

            # Bugungi kunda shartnomachi savdo kiritganmi tekshirish
            cursor.execute("SELECT * FROM daily_sales WHERE user_id = %s AND sale_date = %s", (user_id, today))
            existing_sale = cursor.fetchone()

            if existing_sale:
                # Agar savdo bor bo'lsa, xabar yuborish
                await message.reply("Bugun siz allaqachon savdo kiritdingiz. Iltimos, ertaga yana urinib ko'ring.")
            else:
                # Jami savdolarni hisoblash
                cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
                total_sales = cursor.fetchone()[0]

                if total_sales:
                    # Maqsadni olish
                    cursor.execute("SELECT target FROM users WHERE id = %s", (user_id,))
                    target = cursor.fetchone()[0]

                    # Reja bajarilish foizi
                    percent = (total_sales / target) * 100

                    # Savdo kiritish
                    cursor.execute("INSERT INTO daily_sales (user_id, sales, sale_date, percent) VALUES (%s, %s, %s, %s)",
                                (user_id, sales_value, today, percent))
                    connection.commit()
                else:
                    cursor.execute("INSERT INTO daily_sales (user_id, sales, sale_date) VALUES (%s, %s, %s)",
                                   (user_id, sales_value, today))
                    connection.commit()

                    cursor.execute("select target from users where id = %s", (user_id,))
                    target = cursor.fetchone()[0]

                    cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
                    total_sales = cursor.fetchone()[0]


                    # cursor.execute("select percent from daily_sales where id = %s", (user_id,))
                    # old_percent = cursor.fetchone()

                    percent = (total_sales / target) * 100

                    cursor.execute("UPDATE daily_sales SET percent = %s WHERE user_id = %s and percent = 0.00", 
                                   (percent, user_id))
                    connection.commit()

                # Oylik hisobotni kiritish
                # cursor.execute(
                #     "INSERT INTO monthly_reports (user_id, month, year, total_sales, percent, day) VALUES (%s, %s, "
                #     "%s, %s, %s, %s)",
                #     (user_id, today.month, today.year, total_sales, percent, today.day))
                # connection.commit()
                if percent >= 100:
                    # Ma'lumotlarni `monthly_reports` jadvaliga qo'shish
                    cursor.execute("INSERT INTO monthly_reports (user_id, month, year, total_sales, percent, "
                                   "day) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, today.month, today.year,
                                                                            total_sales, percent, today.day))
                    connection.commit()

                    # `daily_sales` jadvalidan tozalash
                    cursor.execute("DELETE FROM daily_sales WHERE user_id = %s", (user_id,))
                    connection.commit()

                    # Yangi savdo kiritish boshlanishi haqida xabar yuborish
                    await message.reply(
                        "Reja 100% bajarildi! Yangi oy uchun savdo boshlanadi. Yangi savdolarni kiritish mumkin.")

                # Darajani aniqlash
                if total_sales < 26000:
                    degree = "✔️"
                elif 26000 <= total_sales < 52000:
                    degree = "☑️"
                else:
                    degree = "✅"

                # Joriy sana va vaqtni olish
                datetimes = datetime.datetime.now()
                date = datetimes.strftime("%Y-%m-%d")
                time = datetimes.strftime("%H:%M:%S")

                cursor.execute("SELECT name FROM users WHERE telegram_id = %s", (message.from_user.id,))
                name = cursor.fetchone()

                message_text = (f"{date} | {time}\n\n"
                                f"👤: {name[0]}\n🆔: {message.from_user.id}\n\n"
                                f"Savdo qo'shildi 💰: {sales_value}$.\n"
                                f"Jami savdo 💹: {total_sales}$.\nReja: {percent:.2f}% bajarildi {degree}")

                await message.reply(message_text)

                await bot.send_message(chat_id="-1002293235387", text=message_text)

                cursor.close()
                connection.close()
        else:
            await message.reply("Savdoni faqat butun va haqiqiy sonlarda kiriting!")
    else:
        await message.answer("Siz shartnomachi emassiz!")


# Kerakli qismini olish kerak!

# @dp.message_handler()
# async def handle_save_sales(message: types.Message):
#     connection = get_db_connection()
#     cursor = connection.cursor()
#
#     # Foydalanuvchi ma'lumotlarini olish
#     cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
#     user = cursor.fetchone()
#
#     # Foydalanuvchi shartnomachi bo'lsa
#     if user and user[3] == 'contractor':
#         # Faqat raqamlarni qabul qilish
#         if message.text.isdigit() or isinstance(float(message.text), float):
#             sales_value = float(message.text)
#
#             # Foydalanuvchi ID'sini olish
#             cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
#             user_id = cursor.fetchone()[0]
#
#             today = datetime.date.today()
#
#             # Bugungi kunda shartnomachi savdo kiritganmi tekshirish
#             cursor.execute("SELECT * FROM daily_sales WHERE user_id = %s AND date = %s", (user_id, today))
#             existing_sale = cursor.fetchone()
#
#             if existing_sale:
#                 # Agar savdo bor bo'lsa, xabar yuborish
#                 await message.reply("Bugun siz allaqachon savdo kiritdingiz. Iltimos, ertaga yana urinib ko'ring.")
#             else:
#                 # Savdo kiritish
#                 cursor.execute("INSERT INTO daily_sales (user_id, sales, date) VALUES (%s, %s, %s)",
#                                (user_id, sales_value, today))
#                 connection.commit()
#
#                 # Jami savdolarni hisoblash
#                 cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
#                 total_sales = cursor.fetchone()[0]
#
#                 # Maqsadni olish
#                 cursor.execute("SELECT target FROM users WHERE id = %s", (user_id,))
#                 target = cursor.fetchone()[0]
#
#                 # Reja bajarilish foizi
#                 percent = (total_sales / target) * 100
#
#                 # Har bir kiritilgan savdo haqida hisobot yuborish
#                 await message.reply(
#                     f"Bugungi savdo qo'shildi: {sales_value}$.\n"
#                     f"Jami savdo: {total_sales}$.\n"
#                     f"Reja: {percent:.2f}% bajarildi."
#                 )
#
#                 # Agar 100% bajarilsa, ma'lumotlarni `monthly_reports` ga qo'shish
#                 if percent >= 100:
#                     # Ma'lumotlarni `monthly_reports` jadvaliga qo'shish
#                     cursor.execute(
#                         "INSERT INTO monthly_reports (user_id, month, year, total_sales, percent, day) VALUES (%s, %s, %s, %s, %s, %s)",
#                         (user_id, today.month, today.year, total_sales, percent, today.day))
#                     connection.commit()
#
#                     # Darajani aniqlash
#                     if total_sales < 26000:
#                         degree = "✔️"
#                     elif 26000 <= total_sales < 52000:
#                         degree = "☑️"
#                     else:
#                         degree = "✅"
#
#                     # Joriy sana va vaqtni olish
#                     datetimes = datetime.datetime.now()
#                     date = datetimes.strftime("%Y-%m-%d")
#                     time = datetimes.strftime("%H:%M:%S")
#
#                     cursor.execute("SELECT name FROM users WHERE telegram_id = %s", (user_id,))
#                     name = cursor.fetchone()[0]
#
#                     # Hisobot yuborish
#                     await message.reply(
#                         f"{date} | {time}\n\n"
#                         f"👤: {name}\n🆔: {message.from_user.id}\n\n"
#                         f"Savdo qo'shildi 💰: {sales_value}$.\n"
#                         f"Jami savdo 💹: {total_sales}$.\nReja: {percent:.2f}% bajarildi {degree}"
#                     )
#
#                     # `daily_sales` jadvalidan tozalash
#                     cursor.execute("DELETE FROM daily_sales WHERE user_id = %s AND date = %s", (user_id, today))
#                     connection.commit()
#
#                     # Yangi oyga o'tish uchun maqsadni yangilash (masalan, maqsadni yangilash)
#                     cursor.execute("UPDATE users SET target = target + 10000 WHERE id = %s", (user_id,))
#                     connection.commit()
#
#                     # Yangi savdo kiritish boshlanishi haqida xabar yuborish
#                     await message.reply(
#                         "Reja 100% bajarildi! Yangi oy uchun savdo boshlanadi. Yangi savdolarni kiritish mumkin.")
#
#                 cursor.close()
#                 connection.close()
#
#         else:
#             await message.reply("Savdoni faqat butun va haqiqiy sonlarda kiriting!")
#     else:
#         await message.answer("Siz shartnomachi emassiz!")
