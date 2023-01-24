from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from tgbot.interfaces.connector_bitrix import \
    EmployeeDoesNotExist, DatabaseError
from tgbot.services.account_promoter import Promoter
from tgbot.services.account_manager import Manager
from tgbot.utils.broadcast import send_messages
from tgbot.config import TG_ADMINS_ID


class AccessMiddleware(BaseMiddleware):

    async def on_pre_process_message(
            self, message: types.Message, data: dict, *arg, **kwargs):
        user_from_tg = types.User.get_current()
        tg_id = user_from_tg.id
        logger.info(f'user_from_tg: {tg_id}')
        load_answer = await message.answer('Загружаю...')
        try:
            promoter = await Promoter.get(str(tg_id))
        except EmployeeDoesNotExist:
            await send_messages(
                TG_ADMINS_ID,
                f'Promoter EmployeeDoesNotExist {tg_id}')
            promoter = None
        except DatabaseError:
            await send_messages(
                TG_ADMINS_ID,
                f'Promoter DatabaseError {tg_id}')
            promoter = None

        if isinstance(promoter, Promoter):
            logger.info(f'promoter: {await promoter.get_vr_code()}')
            data['promoter'] = promoter
        else:
            await message.answer('Пройдите регистрацию')
            CancelHandler()
            return

        try:
            manager = await Manager.get(str(tg_id))
        except EmployeeDoesNotExist:
            # await send_messages(
            #     TG_ADMINS_ID,
            #     f'Manager EmployeeDoesNotExist {tg_id}')
            manager = None
        except DatabaseError:
            await send_messages(
                TG_ADMINS_ID,
                f'Manager DatabaseError {tg_id}')
            manager = None

        if isinstance(manager, Manager):
            logger.info(f'manager: {await manager.get_vr_code()}')
        data['manager'] = manager

        await load_answer.delete()
