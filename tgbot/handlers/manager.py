from aiogram import types
from aiogram.dispatcher.filters import Text
from loguru import logger

from tgbot.loader import dp
from tgbot.keyboards.registered_user import manager_keyboard
from tgbot.services.account_promoter import Promoter
from tgbot.services.account_manager import Manager
from tgbot.filters.manager import IsManagerUserFilter
# from tgbot.services.salary_calculator.salary_calculator import manager_salary


@dp.message_handler(
    Text(equals='Продажи моей команды сегодня'), IsManagerUserFilter())
async def get_today_team_sales(
        message: types.Message, promoter: Promoter, manager: Manager):
    logger.info(f'manager: {await manager.get_vr_code()}')
    answer_message = await message.answer('Загружаю ...')
    count_sales = await manager.get_sales_by_every_promoter()
    vr_code = await manager.get_vr_code()
    text = f'<b>{vr_code}</b>\nПродажи вашей команды\n'
    for promoter, count in count_sales:
        line = (
            f'\n{await promoter.get_name(short=True)} '
            f'({await promoter.get_vr_code()}): <b>{count}</b>'
        )
        text += line

    await answer_message.edit_text(text)


@dp.message_handler(
    Text(equals='Продажи моей команды за неделю'), IsManagerUserFilter())
async def get_team_week_sales(
        message: types.Message, promoter: Promoter, manager: Manager):
    logger.info(f'manager: {await manager.get_vr_code()}')


@dp.message_handler(
    Text(equals='Моя команда'), IsManagerUserFilter())
async def get_team(
        message: types.Message, promoter: Promoter, manager: Manager):
    logger.info(f'manager: {await manager.get_vr_code()}')

    answer_message = await message.answer('Загружаю ...')
    promoters = await manager.get_promoters()
    vr_code = await manager.get_vr_code()
    text = f'<b>{vr_code}</b>\nВаша команда\n'
    for promoter in promoters:
        line = (
            f'\n{await promoter.get_name(short=False)} '
            f'({await promoter.get_vr_code()})'
        )
        text += line

    await answer_message.edit_text(text)
