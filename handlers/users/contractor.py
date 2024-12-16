from aiogram import types

from loader import dp
from handlers.users.admin import get_db_connection
from data.config import ADMINS
import datetime


# Add Contractor function
def add_contractor(contractor_id, full_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'contractor')",
                   (contractor_id, full_name))
    conn.commit()


def delete_contractor(contractor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("delete from users where telegram_id = %s", (contractor_id,))
    conn.commit()


@dp.message_handler(commands="add_contractor")
async def handle_add_contractor(message: types.Message):
    if int(message.from_user.id) != int(ADMINS[0]):
        print(ADMINS)
        return await message.reply("Siz admin emassiz.")
    else:
        split_text = message.text.split(' ')
        if len(split_text) >= 2:
            if split_text[1].isdigit():
                contractor_id = split_text[1]
                contractor_name = " ".join(split_text[2:])
                add_contractor(contractor_id=contractor_id, full_name=contractor_name)
                await message.reply(
                    f"{contractor_name} [ {contractor_id} ] shartnomachi sifatida muvaffaqiyatli qo'shildi.")
            else:
                await message.reply(f"Shartnomachi IDsi [ {split_text[1]} ] xato! \nFaqat raqamlardan iborat bo'lishi "
                                    f"kerak!\n\n"
                                    f"Quyidagicha kiriting:\n"
                                    f"/add_contractor 123456789 John Smith\n")
        else:
            await message.reply("Shartnomachi ismi va ID si kiritilmadi!\n\n"
                                "Quyidagicha kiriting:\n"
                                "/add_contractor 123456789 John Smith\n")


@dp.message_handler(commands="delete_contractor")
async def handler_delete_contractor(message: types.Message):
    if int(message.from_user.id) != int(ADMINS[0]):
        return await message.reply("Siz admin emassiz.")
    else:
        split_text = message.text.split(' ')
        if len(split_text) >= 2:
            if split_text[1].isdigit():
                contractor_id = split_text[1]
                delete_contractor(contractor_id=contractor_id)
                await message.reply(
                    f"Shartnomachi ID [ {contractor_id} ] muvaffaqiyatli o'chirildi.")
            else:
                await message.reply(f"Shartnomachi IDsi [ {split_text[1]} ] xato! \nFaqat raqamlardan iborat bo'lishi "
                                    f"kerak!")
        else:
            await message.reply("Shartnomachi ID si kiritilmadi!\n\n"
                                "Quyidagicha kiriting:\n"
                                "/delete_contractor 123456789\n")


@dp.message_handler(commands="change_last")
async def changing_last_money(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
    user_id = cursor.fetchone()

    if user_id:
        cursor.execute("SELECT sales FROM daily_sales WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id[0],))
        last_sale = cursor.fetchone()
        if last_sale:
            last_sale_value = last_sale[0]
            today = datetime.date.today()

            split_text = message.text.split(' ')
            if len(split_text) == 2:
                new_sale_value = split_text[1]

                if new_sale_value.replace('.', '', 1).isdigit():
                    new_sale_value = float(new_sale_value)

                    if last_sale_value != new_sale_value:
                        cursor.execute(
                            "UPDATE daily_sales SET sales = %s WHERE user_id = %s AND sales = %s",
                            (new_sale_value, user_id[0], last_sale_value)
                        )
                        conn.commit()
                        await message.reply(f"Oxirgi kiritilgan savdo {last_sale_value}$ "
                                            f"{new_sale_value}$ ga o'zgartirildi.")
                    else:
                        await message.reply(f"O'zgartirilgan savdo miqdori oxirgi savdo miqdoriga teng bo'lishi "
                                            f"mumkin emas!\nOxirgi savdo: {last_sale_value}$")
                else:
                    await message.reply("Savdoni faqat butun va haqiqiy sonlarda kiriting!")
            else:
                await message.reply("Ma'lumotlar to'g'ri kiritilmadi!")
        else:
            await message.reply("Savdo ma'lumotlari topilmadi.")
    else:
        await message.reply("Siz shartnomachi emassiz!")

    cursor.close()
    conn.close()
