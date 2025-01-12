from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_btns():
    btns = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text="Shartnomachi ➕"), KeyboardButton(text="Shartnomachini ➖")],
            [KeyboardButton(text="Hisobotlar")],
        ], resize_keyboard=True
    )
    return btns


def contractor_btns():
    btns = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text="Savdo kiritishni boshlash")],
        ], resize_keyboard=True
    )
    return btns


def menu_btn():
    btns = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text="Bosh menyuga qaytish")]
        ], resize_keyboard=True
    )
    return btns