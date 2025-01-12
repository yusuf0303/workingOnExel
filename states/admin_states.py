from aiogram.dispatcher.filters.state import State, StatesGroup


class ADMINMENU(StatesGroup):
    start_menu = State()
    adding_contractor = State()
    contractor_name = State()
    delete_contractor = State()

