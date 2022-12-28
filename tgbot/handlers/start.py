from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from tgbot.loader import dp
from tgbot.keyboards.registered_user import promoter_keyboard, manager_keyboard
from tgbot.services.account_promoter import Promoter
from tgbot.services.account_manager import Manager


@dp.message_handler(CommandStart(), state='*')
async def start_menu_handler(
        message: types.Message, promoter: Promoter, manager: Manager):

    if isinstance(manager, Manager):
        role_name = 'Cупервайзер'
    else:
        role_name = 'Промоутер'

    text = (
        f'Вы успешно авторизированы \n'
        f'ФИО: {await promoter.get_name()}\n'
        f'Ваш vr код: {await promoter.get_vr_code()}\n'
        f'Ваша должность: {role_name}\n'
    )
    await message.answer(text, reply_markup=promoter_keyboard)
