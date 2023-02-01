from __future__ import annotations
import asyncio
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from loguru import logger

from tgbot.interfaces.connector_sales_base import ConnectorSalesBase, SaleEntry
from tgbot.interfaces.connector_bitrix import ConnectorBitrix
from tgbot.interfaces.connector_gs_plan import PlanSheet
from tgbot.services.account_utils import WorkWeekMixin
from tgbot.services.account_promoter import Promoter


class Manager(WorkWeekMixin):
    _sale_base: ConnectorSalesBase = ConnectorSalesBase()
    _plan_sheet: PlanSheet = PlanSheet()
    _instanse_cache = {}

    @classmethod
    async def get(cls, tg_id: str) -> Manager:
        if tg_id not in cls._instanse_cache:
            manager = await cls.create(tg_id)
            cls._instanse_cache[tg_id] = manager

        return cls._instanse_cache.get(tg_id)

    @classmethod
    async def create(cls, tg_id: str = None, vr_code: str = None) -> Manager:
        manager_dict = await ConnectorBitrix().get_manager(
            tg_id=tg_id,
            ref_code=vr_code)
        self = Manager()
        self._tg_id: str = tg_id
        self._vr_code: str = manager_dict.get(ConnectorBitrix.REF_CODE)
        self._manager_id: str = manager_dict.get(ConnectorBitrix.MANAGER_ID)
        self._promoter: Promoter = await Promoter.get_by_vr(self._vr_code)
        logger.info(f'manager {self._vr_code} was created')
        return self

    @classmethod
    async def get_by_manager_id(cls, manager_id: str) -> Manager:
        for _, manager in cls._instanse_cache.items():
            if manager._manager_id == manager_id:
                return manager
        return None

    @classmethod
    async def get_by_vr(cls, vr_code: str) -> Manager:
        for _, manager in cls._instanse_cache.items():
            if manager._vr_code == vr_code:
                return manager

        manager = await cls.create(vr_code=vr_code)
        if manager._tg_id:
            cls._instanse_cache[manager._tg_id] = manager
        return manager

    @classmethod
    async def clear_cache(cls):
        cls._instanse_cache.clear()

    def __init__(self) -> None:
        pass

    async def get_vr_code(self) -> str:
        """return vrcode str: 'vr000000"""
        return self._vr_code

    async def get_city(self) -> str:
        return await self._promoter.get_city()

    async def get_tg_id(self) -> str:
        return self._tg_id

    async def get_manager_id(self) -> str:
        return self._manager_id

    async def is_region(self) -> bool:
        if self._promoter.get_city() == 'Санкт-Петербург':
            return False
        else:
            return True

    async def send_notification(self):
        pass

    async def get_sales(self):
        pass

    async def get_vr_list_promoters(self) -> List[str]:
        promoters_list = await ConnectorBitrix().get_promoters_by_manager(
            manager_id=await self.get_manager_id())
        vr_list = []
        for promoter_dict in promoters_list:
            vr_list.append(
                promoter_dict.get(ConnectorBitrix.REF_CODE))
        return vr_list

    async def get_promoters(self) -> List[Promoter]:
        """Получить промоутеров этого менеджера

        Returns:
            List: [ Promoter, ... ]
        """
        vr_list = await self.get_vr_list_promoters()

        tasks = [Promoter.get_by_vr(vr_code) for vr_code in vr_list]
        promoters = await asyncio.gather(*tasks)
        return promoters

    async def get_sales_of_team(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple]:
        """Возвращает продажи команды менеджера. По каждому промоутеру

        Args:
            start_date (datetime): _description_
            end_date (datetime): _description_

        Returns:
            List: [
                (Promoter, { date: List[Ticket] } ),
                ...
            ]
        """
        promoters = await self.get_promoters()

        async def make_tuple(promoter: Promoter):
            tickets_dict = await promoter.get_sold_tickets(
                start_date=start_date,
                end_date=end_date
            )
            return (promoter, tickets_dict)

        tasks = [make_tuple(promoter) for promoter in promoters]
        result_list = await asyncio.gather(*tasks)

        return result_list

    async def get_sales_of_team_on_this_week(self) -> List[Tuple]:
        """
        Returns:
            List: [
                (Promoter, { date: List[Ticket] } ),
                ...
            ]
        """
        result_list = await self.get_sales_of_team(
            start_date=self.get_first_day_of_week(),
            end_date=self.get_today()
        )
        return result_list

    async def get_sales_of_team_on_last_week(self) -> Dict:
        first_day = self.get_first_day_of_week()
        start_date = first_day - timedelta(days=7)
        end_date = first_day - timedelta(days=1)
        count_dict = await self.get_sales_of_team(
            start_date=start_date,
            end_date=end_date
        )
        return count_dict

    async def get_returned_sales_of_team_on_this_week(self) -> List[SaleEntry]:
        """_summary_

        Returns:
            List[SaleEntry]: _description_
        """
        result_list: List[SaleEntry] = await self._sale_base.get_all_sales(
            start_date=self.get_first_day_of_week(),
            end_date=self.get_today(),
            status='return'
        )
        return result_list

    async def get_plan(
        self, start_date: datetime, end_date: datetime = None
    ) -> dict:
        """Возвращает план по дням

        Args:
            start_date (datetime): _description_
            end_date (datetime, optional): _description_. Defaults to None.

        Returns:
            dict[]: {date: float}
        """
        plan = self._plan_sheet.get_manager_plan(
            city_name=await self.get_city(),
            start_date=start_date.date(),
            end_date=end_date.date()
        )
        if not end_date:
            end_date = start_date
        delta = end_date - start_date
        result = {
            (start_date+timedelta(days=i)).date(): plan[i]
            for i in range(delta.days + 1)
        }

        return result

    async def get_plan_on_this_week(self) -> dict:
        """Возвращает план по дням
        Returns:
            dict: {date: float, }
        """
        result = await self.get_plan(
            start_date=self.get_first_day_of_week(),
            end_date=self.get_last_day_of_week()
        )
        return result


async def example():
    webhook_b = 'https://int-active.bitrix24.ru/rest/193/i3qfdc3z8jygp5pp/'
    await ConnectorBitrix.setup(webhook_b)
    await Promoter.startup()
    promoter = Promoter('98244574')
    await promoter.get_count_of_sales_on_last_week()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example())
