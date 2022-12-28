from aiogram import types
from aiogram.dispatcher.filters import Filter
from aiogram.dispatcher.handler import ctx_data

from tgbot.services.account_manager import Manager


class IsManagerUserFilter(Filter):

    async def check(self, message: types.Message, *args, **kwargs) -> bool:
        data = ctx_data.get()
        manager = data.get('manager')
        return bool(isinstance(manager, Manager))
