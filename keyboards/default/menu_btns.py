from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Admin menyusi
def admin_btn():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = KeyboardButton("Shartnomachi qo'shish")
    button_2 = KeyboardButton("Shartnomachini o'chirish")
    button_3 = KeyboardButton("Hisobotlar")
    keyboard.add(button_1, button_2).add(button_3)
    return keyboard


# Menu
def menu_btn():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = KeyboardButton("Menyuga qaytish")
    keyboard.add(button_1)
    return keyboard
