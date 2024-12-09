from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from loader import dp
from handlers.users.admin import add_admin, is_contractors, in_list, get_db_connection
from keyboards.default.menu_btns import admin_btn, menu_btn
from data.config import ADMINS


admin_command = [
            types.BotCommand("start", "Botni ishga tushurish"),
            types.BotCommand("reports", "Hisobotlarni chiqarish"),
            types.BotCommand("add_contractor", "Shartnomachi qo'shish"),
            types.BotCommand("delete_contractor", "Shartnomachini o'chirish"),
        ]


@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select name from users where telegram_id = %s", (user_id,))
    username = cursor.fetchone()

    if in_list(user_id=user_id) and str(is_contractors(user_id=user_id)) == 'contractor':
        await dp.bot.set_my_commands(
            [
                types.BotCommand("start", "Botni ishga tushurish"),
                types.BotCommand("reports", "Hisobotlarni chiqarish"),
            ]
        )
        await message.reply(f"Assalomu alaykum, {username[0]}! Savdoning miqdorini kiritishingiz mumkin.")
    else:
        if in_list(user_id=user_id) and str(is_contractors(user_id=user_id)) == 'admin':
            await dp.bot.set_my_commands(
                admin_command
            )
            await message.reply(f"Assalomu alaykum, {username[0]}! Admin menyusiga muvaffaqiyatli kirdingiz.", reply_markup=admin_btn())
        elif int(user_id) == int(ADMINS[0]):
            add_admin(user_id=user_id, full_name=full_name)
            await dp.bot.set_my_commands(
                admin_command
            )
            await message.reply(f"Assalomu alaykum, {username[0]}! Admin hisobiga muvaffaqiyatli ro'yxatdan o'tdingiz.", reply_markup=admin_btn())
        else:
            await dp.bot.set_my_commands(
                [types.BotCommand("start", "Botni ishga tushurish"),]
            )
            await message.reply(f"{message.from_user.full_name}, sizning botdan foydalanishingiz cheklangan 🚫. \n"
                                f"Admin bilan bog'laning.")
