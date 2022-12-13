from __future__ import annotations
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta
from loguru import logger

from tgbot.interfaces.connector_sales_base import ConnectorSalesBase, SaleEntry
from tgbot.interfaces.connector_bitrix import ConnectorBitrix
from tgbot.services.account_utils import WorkWeekMixin


class Promoter(WorkWeekMixin):
    _sale_base: ConnectorSalesBase = ConnectorSalesBase()
    _instanse_cache = {}

    @classmethod
    async def get(cls, tg_id: str) -> Promoter:
        if tg_id not in cls._instanse_cache:
            promoter = await cls.create(tg_id)
            cls._instanse_cache[tg_id] = promoter
        return cls._instanse_cache[tg_id]

    @classmethod
    async def get_by_vr(cls, vr_code: str) -> Promoter:
        for _, promoter in cls._instanse_cache.items():
            if promoter._vr_code == vr_code:
                return promoter

        promoter = await cls.create(vr_code=vr_code)
        if promoter._tg_id:
            cls._instanse_cache[promoter._tg_id] = promoter
        return promoter

    @classmethod
    async def create(cls, tg_id: str = None, vr_code: str = None) -> Promoter:
        promoter_dict = await ConnectorBitrix().get_promoter(
            tg_id=tg_id,
            ref_code=vr_code)

        self = Promoter()
        self._tg_id: str = promoter_dict.get(ConnectorBitrix.TG_ID)
        self._vr_code: str = promoter_dict.get(ConnectorBitrix.REF_CODE)
        self._city: str = promoter_dict.get(ConnectorBitrix.CITY)
        logger.info(f'Promoter {self._vr_code} was created')
        return self

    def __init__(self) -> None:
        pass

    async def get_manager_id(self):
        pass

    async def get_vr_code(self) -> str:
        """return vrcode str: 'vr000000"""
        return self._vr_code

    async def get_city(self) -> str:
        return self._city

    async def get_tg_id(self) -> str:
        return self._tg_id

    async def is_region(self) -> bool:
        if self._city == 'Санкт-Петербург':
            return False
        else:
            return True

    async def send_notification(self):
        pass

    async def get_sales(self):
        pass

    async def get_this_week_sales(self) -> List[SaleEntry]:
        """Возвращает продажи за последнюю неделю. С момента дня выплат.

        Returns:
            List[SaleEntry]: []
        """
        sales: List[SaleEntry] = await self._sale_base.get_sales_by_promoter(
            vr_code=await self.get_vr_code(),
            start_date=self.get_first_day_of_week(),
            end_date=self.get_today()
        )
        return sales

    async def get_count_of_sales(
        self, start_date: datetime, end_date: datetime = None
    ):
        """_summary_

        Args:
            start_date (datetime): _description_
            end_date (datetime): _description_

        Returns:
            dict: {date: count, date: count, }
        """
        sales: List[SaleEntry] = await self._sale_base.get_sales_by_promoter(
            vr_code=await self.get_vr_code(),
            start_date=start_date,
            end_date=end_date
        )
        if not end_date:
            end_date = start_date
        delta = end_date - start_date
        count_dict = {
            (start_date+timedelta(days=i)).date(): 0
            for i in range(delta.days + 1)
        }
        for sale in sales:
            count_dict[sale.sale_time.date()] += sale.count
        return count_dict

    async def get_count_of_sales_on_this_week(self) -> Dict:
        count_dict = await self.get_count_of_sales(
            start_date=self.get_first_day_of_week(),
            end_date=self.get_today()
        )
        return count_dict

    async def get_count_of_sales_on_last_week(self) -> Dict:
        first_day = self.get_first_day_of_week()
        start_date = first_day - timedelta(days=7)
        end_date = first_day - timedelta(days=1)
        count_dict = await self.get_count_of_sales(
            start_date=start_date,
            end_date=end_date
        )
        return count_dict


async def example():
    webhook_b = 'https://int-active.bitrix24.ru/rest/193/i3qfdc3z8jygp5pp/'
    await ConnectorBitrix.setup(webhook_b)
    await Promoter.startup()
    promoter = Promoter('98244574')
    await promoter.get_count_of_sales_on_last_week()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example())
