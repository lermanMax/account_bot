from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def promoter_markup() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('Мои продажи')
            ],
            [
                KeyboardButton('Мои продажи на прошлой неделе')
            ],
        ]
    )
    return keyboard


def manager_markup() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('Продажи моей команды сегодня')
            ],
            [
                KeyboardButton('Продажи моей команды за неделю')
            ],
        ]
    )
    return keyboard


promoter_keyboard = promoter_markup()
manager_keyboard = manager_markup()
