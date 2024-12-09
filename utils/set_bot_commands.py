from aiogram import types

from handlers.users.admin import get_db_connection


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish"),
        ]
    )

