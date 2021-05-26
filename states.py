from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    loading_restaurant_events = State()
