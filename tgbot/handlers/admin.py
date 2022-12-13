from aiogram import types
from aiogram.dispatcher.filters import Text
from loguru import logger

from tgbot.loader import dp
from tgbot.services.account_promoter import Promoter
from tgbot.services.account_manager import Manager
from tgbot.handlers.promoter import get_this_week_sales
from tgbot.handlers.manager import get_today_team_sales, get_team

"""
@dp.message_handler()
async def get_sales(
        message: types.Message):
    logger.info(f'message: {message.text}')
    await get_today_team_sales(
        message=message,
        promoter=await Promoter.get_by_vr(vr_code=message.text),
        manager=await Manager.get_by_vr(vr_code=message.text)
    )

"""
@dp.message_handler()
async def get_sales(
        message: types.Message):
    logger.info(f'message: {message.text}')
    await get_this_week_sales(
        message=message,
        promoter=await Promoter.get_by_vr(vr_code=message.text)
    )

