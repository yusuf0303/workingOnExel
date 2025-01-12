from aiogram import types

from loader import dp
from handlers.users.admin import get_db_connection
from data.config import ADMINS
import datetime
from aiogram.dispatcher import FSMContext
from states.admin_states import ADMINMENU
from states.contractor_states import CONTRACTOR
from aiogram.dispatcher.filters import Text
from keyboards.default.menu_btns import admin_btns, contractor_btns, menu_btn
from handlers.users.functions import *


@dp.message_handler(Text(equals="Bosh menyuga qaytish"), state="*")
async def go_to_main_menu(message: types.Message, state: FSMContext):
    if int(message.from_user.id) == int(ADMINS[0]): 
        await message.answer("Bosh menyu", reply_markup=admin_btns())
        await ADMINMENU.start_menu.set()
    else:
        await message.answer("Bosh menyu", reply_markup=contractor_btns())
        await CONTRACTOR.start_menu.set()


@dp.message_handler(Text(equals="Shartnomachi ➕"), state=ADMINMENU.start_menu)
async def handle_add_contractor(message: types.Message, state: FSMContext):
    await message.answer("Shartnomachi qo'shish uchun uning ID sini yuboring 👇", reply_markup=menu_btn())
    await ADMINMENU.adding_contractor.set()


@dp.message_handler(state=ADMINMENU.adding_contractor)
async def handle_add_contractor(message: types.Message, state: FSMContext):
    if int(message.from_user.id) != int(ADMINS[0]):
        print(ADMINS)
        return await message.reply("Siz admin emassiz.")
    else:
        if is_valid_telegram_id(telegram_id=message.text):
            contractor_id = message.text
            async with state.proxy() as adding_contraactor:
                adding_contraactor['id'] = contractor_id
            await message.reply(
                f"🆔: {contractor_id} ✅\nShartnomachi ismi (familyasi)ni kiriting 👇")
            await ADMINMENU.contractor_name.set()
        else:
            await message.reply(f"Shartnomachi IDsi [ {message.text} ] xato! \nFaqat raqamlardan iborat bo'lishi kerak!")


@dp.message_handler(state=ADMINMENU.contractor_name)
async def handle_contractor_name(msg: types.Message, state: FSMContext):
    if msg.text.isalpha:
        async with state.proxy() as adding_contractor:
            adding_contractor['name'] = msg.text

        contractor_id = adding_contractor['id']
        contractor_name = adding_contractor['name']

        if add_contractor(contractor_id=contractor_id, full_name=contractor_name) == True:
            await msg.answer(f"{contractor_name} [{contractor_id}] shartnomachi sifatida muvaffaqiyatli qo'shildi ✅", reply_markup=admin_btns())
            await ADMINMENU.start_menu.set()
        else:
            await msg.answer("Ushbu id oldinroq ro'yxatdan o'tgan. Boshqa id bilan urinib ko'ring.")
            await ADMINMENU.adding_contractor.set()
    else:
        await msg.answer(f"Shartnomachi ismi xato [{msg.text}]! Ism familya faqat harflardan iborat bo'lishi kerak!")


@dp.message_handler(Text(equals="Shartnomachini ➖"), state=ADMINMENU.start_menu)
async def handler_delete_contractor(message: types.Message, state: FSMContext):
    await message.answer("Shartnomachini o'chirish uchun uning ID sini yuboring 👇", reply_markup=menu_btn())
    await ADMINMENU.delete_contractor.set()


@dp.message_handler(state=ADMINMENU.delete_contractor)
async def handle_deleting_contractor_id(message: types.Message, state: FSMContext):
    if int(message.from_user.id) != int(ADMINS[0]):
        return await message.reply("Siz admin emassiz.")
    else:
        if is_valid_telegram_id(telegram_id=message.text):
            contractor_id = int(message.text)
            if delete_contractor(contractor_id=contractor_id) == True:
                await message.reply(
                    f"Shartnomachi ID [ {contractor_id} ] muvaffaqiyatli o'chirildi.", reply_markup=admin_btns())
                await ADMINMENU.start_menu.set()
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("select telegram_id, name from users")
                datas = cursor.fetchall()
                contractors_list = "Ro'yxatdagi shartnomachilar:\n"
                for user in datas:
                    contractors_list += f"{user[1]} [<code> {user[0]} </code>]\n"
                await message.answer(f"Ushbu id ro'yxatda mavjud emas!\n\n{contractors_list}", parse_mode="HTML")
        else:
            await message.reply(f"Shartnomachi IDsi [ {message.text} ] xato! \nFaqat raqamlardan iborat bo'lishi kerak!")


# @dp.message_handler(Text(equals="Oxirgi sotuvni o'zgartirish"), state=CONTRACTOR.start_menu)
# async def changing_last_money(message: types.Message):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
#     user_id = cursor.fetchone()

#     if user_id:
#         cursor.execute("SELECT sales FROM daily_sales WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id[0],))
#         last_sale = cursor.fetchone()
#         if last_sale:
#             last_sale_value = last_sale[0]
#             today = datetime.date.today()

#             await message.answer(f"Oxirgi kiritgan savdoingiz: [{last_sale_value}]\nO'zgartirish uchun yangi savdo miqdorini yuboring")



#             new_sale_value = float(message.text)

#             if last_sale_value != new_sale_value:
#                 cursor.execute(
#                     "UPDATE daily_sales SET sales = %s WHERE user_id = %s AND sales = %s",
#                     (new_sale_value, user_id[0], last_sale_value)
#                 )
#                 conn.commit()
#                 await message.reply(f"Oxirgi kiritilgan savdo {last_sale_value}$ "
#                                     f"{new_sale_value}$ ga o'zgartirildi.")
#             else:
#                 await message.reply(f"O'zgartirilgan savdo miqdori oxirgi savdo miqdoriga teng bo'lishi "
#                                     f"mumkin emas!\nOxirgi savdo: {last_sale_value}$")
#         else:
#             await message.reply("Savdo ma'lumotlari topilmadi.")
#     else:
#         await message.reply("Siz shartnomachi emassiz!")

#     cursor.close()
#     conn.close()
