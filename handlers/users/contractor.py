from aiogram import types

from loader import dp
from keyboards.default.menu_btns import admin_btn
from handlers.users.admin import get_db_connection
from data.config import ADMINS


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
                    f"{contractor_name} [ {contractor_id} ] shartnomachi sifatida muvaffaqiyatli qo'shildi.",
                    reply_markup=admin_btn())
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
                    f"Shartnomachi ID [ {contractor_id} ] muvaffaqiyatli o'chirildi.",
                    reply_markup=admin_btn())
            else:
                await message.reply(f"Shartnomachi IDsi [ {split_text[1]} ] xato! \nFaqat raqamlardan iborat bo'lishi "
                                    f"kerak!")
        else:
            await message.reply("Shartnomachi ID si kiritilmadi!\n\n"
                                "Quyidagicha kiriting:\n"
                                "/delete_contractor 123456789\n")
