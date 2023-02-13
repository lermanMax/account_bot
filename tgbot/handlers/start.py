from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardRemove

from tgbot.loader import dp
from tgbot.keyboards.registered_user import promoter_keyboard, manager_keyboard
from tgbot.keyboards.phone import phone_keyboard
from tgbot.keyboards.start import start_keyboard
from tgbot.services.account_promoter import Promoter
from tgbot.services.account_manager import Manager
from tgbot.filters.unauthentificated import IsUserUnauthenticatedFilter
from tgbot.filters.promoter import IsPromoterUserFilter
from tgbot.interfaces.connector_bitrix import ConnectorBitrix, \
    EmployeeDoesNotExist, EmployeeAlreadyExist, PhoneAlreadyTaken, DatabaseError
from tgbot.utils.broadcast import send_messages_to_admins


@dp.message_handler(IsPromoterUserFilter(), CommandStart(), state='*')
async def start_menu_handler(
        message: types.Message, promoter: Promoter, manager: Manager):

    if isinstance(manager, Manager):
        role_name = 'Cупервайзер'
    else:
        role_name = await promoter.get_partner_type()

    text = (
        f'Вы успешно авторизированы \n'
        f'ФИО: {await promoter.get_name()}\n'
        f'Ваш vr код: {await promoter.get_vr_code()}\n'
        f'Ваш тип партнерства: {role_name}\n'
    )
    await message.answer(text, reply_markup=promoter_keyboard)


@dp.message_handler(IsUserUnauthenticatedFilter())
async def request_phone(message: types.Message):
    text = (
        'Отправьте номер телефона.'
        '\nНажмите на кнопку "Поделиться номером" 👇👇👇'
    )
    await message.answer(
        text,
        reply_markup=phone_keyboard
    )


@dp.message_handler(content_types=['contact'])
async def get_contact_handler(message: types.Message) -> None:
    phone_number = message.contact.phone_number
    if phone_number.startswith('7'):
        phone_number = '+' + phone_number
    if phone_number.startswith('8'):
        phone_number = '+7' + phone_number[1:]
    text = f'Ваш номер: {phone_number}'
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())

    bitrix = ConnectorBitrix()
    try:
        await bitrix.update_tg_id_by_phone(
            phone=phone_number,
            tg_id=message.from_user.id
        )
        await message.answer(
            'Ваш номер успешно найден. Нажмите /start',
            reply_markup=start_keyboard
        )
    except EmployeeDoesNotExist:
        await message.answer(
            ('Номер не найден.'
             '\nПопробуйте еще раз позже или обратитесь к администратору.'),
            reply_markup=phone_keyboard
        )
    except PhoneAlreadyTaken:
        await message.answer(
            ('Такой номер уже используется другим пользователем.'
             'Если это ваш номер, обратитесь к администратору.'),
            reply_markup=phone_keyboard
        )
    except EmployeeAlreadyExist:
        await message.answer(
            'Нажмите /start',
            reply_markup=start_keyboard
        )
    except DatabaseError:
        await message.answer(
            ('Возникала ошибка в базе данных.'
             '\nАдминистратор уведомлен и приступил к решению.'
             '\nИзвините за неудобства'),
            reply_markup=phone_keyboard
        )
        await send_messages_to_admins(
            f'DatabaseError {phone_number} {message.from_user.id}'
        )
