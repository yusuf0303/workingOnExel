from aiogram.dispatcher.filters.state import State, StatesGroup


class CONTRACTOR(StatesGroup):
    start_menu = State()
    all_sales = State()
    made_contract = State()
    collect_reasons = State()
    collect_reasons_not_made = State()
