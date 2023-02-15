from aiogram import types
from aiogram.dispatcher.filters import Filter
from aiogram.dispatcher.handler import ctx_data

from tgbot.services.account_promoter import Promoter


class IsUserUnauthenticatedFilter(Filter):

    async def check(self, message: types.Message, *args, **kwargs) -> bool:
        data = ctx_data.get()
        promoter = data.get('promoter')
        return bool(promoter is None)
