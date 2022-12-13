from aiogram import types
from aiogram.dispatcher.filters import Text
from loguru import logger

from tgbot.loader import dp
from tgbot.keyboards.registered_user import promoter_keyboard
from tgbot.services.account_promoter import Promoter
from tgbot.services.salary_calculator.salary_calculator import agent_salary


@dp.message_handler(Text(equals='Мои продажи'), )
async def get_this_week_sales(message: types.Message, promoter: Promoter):
    logger.info(f'promoter: {await promoter.get_vr_code()}')
    answer_message = await message.answer('Загружаю ...')

    count_sales: dict = await promoter.get_count_of_sales_on_this_week()
    vr_code = await promoter.get_vr_code()
    text = f'<b>{vr_code}</b>\nВаши продажи\n'
    for sale_time, count in count_sales.items():
        text += f'\n{sale_time}: <b>{count}</b>'

    salary, today_prize = agent_salary(
        [value for value in count_sales.values()],
        is_regional=await promoter.is_region(),
        is_new=True
    )
    text += f'\n\nЗа неделю вы заработали {salary}руб'
    text += f'\nЗа сегодня вы заработали {today_prize}руб'

    await answer_message.edit_text(text)


@dp.message_handler(Text(equals='Мои продажи на прошлой неделе'), )
async def get_last_week_sales(message: types.Message, promoter: Promoter):
    logger.info(f'promoter: {await promoter.get_vr_code()}')
    count_sales: dict = await promoter.get_count_of_sales_on_last_week()
    vr_code = await promoter.get_vr_code()
    text = f'<b>{vr_code}</b>\nВаши продажи\n'
    for sale_time, count in count_sales.items():
        text += f'\n{sale_time}: <b>{count}</b>'

    salary, today_prize = agent_salary(
        [value for value in count_sales.values()],
        is_regional=await promoter.is_region(),
        is_new=False
    )
    text += f'\n\nЗа прошлую неделю вы заработали {salary}руб'

    await message.answer(text, reply_markup=promoter_keyboard)
