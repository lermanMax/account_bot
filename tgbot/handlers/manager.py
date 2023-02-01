from aiogram import types
from aiogram.dispatcher.filters import Text
from loguru import logger

from tgbot.loader import dp
from tgbot.keyboards.registered_user import manager_keyboard
from tgbot.services.account_promoter import Promoter
from tgbot.services.account_manager import Manager
from tgbot.filters.manager import IsManagerUserFilter
from tgbot.services.salary_calculator.salary_calculator import \
    apply_coefficient, manager_salary


@dp.message_handler(
    Text(equals='Продажи моей команды'),
    IsManagerUserFilter())
async def get_today_team_sales(
        message: types.Message, promoter: Promoter, manager: Manager):
    logger.info(f'manager: {await manager.get_vr_code()}')
    answer_message = await message.answer(text='Загружаю ...')

    sales_list = await manager.get_sales_of_team_on_this_week()
    vr_code = await manager.get_vr_code()
    text = f'<b>{vr_code}</b>\nПродажи вашей команды: <b>неделя|сегодня</b>\n'
    sum_week = 0
    sum_today = 0
    for promoter, tickets_by_date in sales_list:
        number_tickets = apply_coefficient(tickets_by_date.values())
        today_sales = number_tickets[-1]
        week_sales = sum(number_tickets)
        sum_today += today_sales
        sum_week += week_sales

        name_line = f'<code>\n{await promoter.get_name(short=True)} '
        vr_line = f'({await promoter.get_vr_code()}): </code>'
        space_line = ' '.join(
            ['' for _ in range(0, 63 - len(name_line) - len(vr_line))])
        sale_line = f'<b>{week_sales}|{today_sales}</b>'

        text += name_line + space_line + vr_line + sale_line

    text += f'\n<b>Итог: {sum_week}|{sum_today}</b>'

    await answer_message.delete()
    await message.answer(text=text, reply_markup=manager_keyboard)


@dp.message_handler(
    Text(equals='Посчитать мое вознаграждение менеджера'),
    IsManagerUserFilter())
async def get_manager_salary(
        message: types.Message, promoter: Promoter, manager: Manager):
    logger.info(f'manager: {await manager.get_vr_code()}')
    answer_message = await message.answer(text='Загружаю ...')

    sales_list = await manager.get_sales_of_team_on_this_week()
    if len(sales_list) == 0:
        await answer_message.edit_text('Ваша команда не найдена')

    vr_code = await manager.get_vr_code()
    tickets = [[] for _ in range(len(sales_list[0][1]))]
    for _, dict_tickets in sales_list:
        promoter_tickets = dict_tickets.values()
        for i, day_tickets in enumerate(promoter_tickets):
            tickets[i].extend(day_tickets)

    week_salary, today_salary = manager_salary(tickets, promoter.is_region())
    text = f'<b>{vr_code}</b>\n'\
           f'Ваше вознаграждение менеджера: \n'\
           f'За эту неделю: <b>{week_salary} руб.</b>\n'\
           f'За сегодня: <b>{today_salary} руб.</b>\n'

    await answer_message.delete()
    await message.answer(text=text, reply_markup=manager_keyboard)


@dp.message_handler(
    Text(equals='Мой План'),
    IsManagerUserFilter())
async def get_plan(
        message: types.Message, promoter: Promoter, manager: Manager):
    logger.info(f'manager: {await manager.get_vr_code()}')
    answer_message = await message.answer(text='Загружаю ...')

    plan = await manager.get_plan_on_this_week()
    vr_code = await manager.get_vr_code()
    text = f'<b>{vr_code}</b>\nПлан на эту неделю\n\n'
    for date, tickets in plan.items():
        text += f'{date}: <b>{tickets}</b>\n'
    text += f'\nИтог: {sum(plan.values())}'
    await answer_message.delete()
    await message.answer(text=text, reply_markup=manager_keyboard)


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


@dp.message_handler(
    Text(equals='Возвраты моей команды'),
    IsManagerUserFilter())
async def get_today_team_returned_sales(
        message: types.Message, promoter: Promoter, manager: Manager):
    logger.info(f'manager: {await manager.get_vr_code()}')
    answer_message = await message.answer(text='Загружаю ...')

    sales_list = await manager.get_returned_sales_of_team_on_this_week()
    vr_code = await manager.get_vr_code()
    text = f'<b>{vr_code}</b>\nВозвраты вашей команды на этой неделе\n'
    for sale in sales_list:
        text += f'\nПроджа №{sale.green_id}\n' \
                f'Билеты: {sale.count}шт. {sale.full_sum}руб\n' \
                f'Дата: {sale.sale_time}\n' \
                f'Промоутер: <code>{sale.vr_code}</code>\n'
    else:
        text += 'возвратов на этой неделе нет'

    await answer_message.edit_text(text)
