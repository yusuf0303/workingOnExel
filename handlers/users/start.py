from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from loader import dp
from handlers.users.admin import add_admin, is_contractors, in_list, get_db_connection
from data.config import ADMINS
from keyboards.default.menu_btns import *
from states.admin_states import ADMINMENU
from states.contractor_states import CONTRACTOR


admin_command = [
            types.BotCommand("start", "Botni ishga tushurish"),
        ]


@dp.message_handler(CommandStart(), state="*")
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    print(user_id)
    full_name = message.from_user.full_name
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select name from users where telegram_id = %s", (user_id,))
    username = cursor.fetchone()

    if in_list(user_id=user_id) and str(is_contractors(user_id=user_id)) == 'contractor':
        await message.answer(f"Assalomu alaykum, {username[0]}! Savdoning miqdorini kiritishingiz mumkin yoki quyidagi tugmalardan birini tanlang 👇", reply_markup=contractor_btns())
        await CONTRACTOR.start_menu.set()
    else:
        if in_list(user_id=user_id) and str(is_contractors(user_id=user_id)) == 'admin':
            await ADMINMENU.start_menu.set()
            await message.reply(f"Assalomu alaykum, {message.from_user.full_name}! Admin menyusiga muvaffaqiyatli kirdingiz.", reply_markup=admin_btns())
        elif int(user_id) == int(ADMINS[0]):
            add_admin(user_id=user_id, full_name=full_name)
            await ADMINMENU.start_menu.set()
            await message.answer(f"Assalomu alaykum, {username[0]}! Admin hisobiga muvaffaqiyatli ro'yxatdan o'tdingiz.", reply_markup=admin_btns())
        else:
            await message.answer(f"{message.from_user.full_name}, sizning botdan foydalanishingiz cheklangan 🚫. \n"
                                f"Admin bilan bog'laning.")
