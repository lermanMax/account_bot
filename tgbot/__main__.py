from aiogram import Dispatcher
from aiogram import executor, types
from loguru import logger
import os

from tgbot.interfaces.connector_bitrix import ConnectorBitrix
from tgbot.config import BITRIX_WEBHOOK
from tgbot.interfaces.connector_sales_base import ConnectorSalesBase
from tgbot.config import SALES_DB_HOST, SALES_DB_PORT, SALES_DB_USER, \
    SALES_DB_PASS, SALES_DB_NAME
from tgbot.interfaces.connector_gs_plan import PlanSheet
from tgbot.config import GSHEET_LINK, GSHEET_SERVICE_FILE
from tgbot.utils.broadcast import send_messages
from tgbot.config import TG_ADMINS_ID


async def setup_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'start')
        ]
    )
    logger.info('Default commands soccessfully set')


async def on_startup_polling(dp: Dispatcher):
    logger.info('Start on polling mode')

    await setup_default_commands(dp)

    from tgbot import handlers

    from tgbot import middlewares

    dp.bitrix_interface = ConnectorBitrix()
    await dp.bitrix_interface.setup(BITRIX_WEBHOOK)

    dp.sale_db_interface = ConnectorSalesBase()
    await dp.sale_db_interface.create_conn(
        host=SALES_DB_HOST,
        port=SALES_DB_PORT,
        user=SALES_DB_USER,
        password=SALES_DB_PASS,
        db=SALES_DB_NAME
    )

    dp.gs_plan_interface = PlanSheet()
    path = f'{os.getcwd()}/tgbot/{GSHEET_SERVICE_FILE}'
    dp.gs_plan_interface.setup(
        gs_url=GSHEET_LINK,
        gs_service_file=path,
    )

    await send_messages(TG_ADMINS_ID, 'startup')


async def on_shutdown(dp: Dispatcher):
    logger.info('Shutdown')

    if hasattr(dp, 'bitrix_interface'):
        await dp.bitrix_interface.shutdown()

    if hasattr(dp, 'sale_db_interface'):
        await dp.sale_db_interface.close()


def polling(skip_updates: bool = False):
    from tgbot.handlers import dp
    executor.start_polling(
        dispatcher=dp,
        skip_updates=skip_updates,
        on_startup=on_startup_polling,
        on_shutdown=on_shutdown
    )


if __name__ == '__main__':
    polling()
