from aiogram import types
from loguru import logger


async def setup_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "войти в личный кабинет"),
        ]
    )
    logger.info('Standard commands are successfully configured')
