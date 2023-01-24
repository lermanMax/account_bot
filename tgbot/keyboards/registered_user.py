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
                KeyboardButton('Продажи моей команды')
            ],
            [
                KeyboardButton('Посчитать мое вознаграждение менеджера')
            ],
        ]
    )
    return keyboard


promoter_keyboard = promoter_markup()
manager_keyboard = manager_markup()
