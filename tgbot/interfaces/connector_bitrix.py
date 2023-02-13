import asyncio
import aiohttp
from typing import List
from datetime import date
from loguru import logger

from fast_bitrix24 import BitrixAsync


class EmployeeDoesNotExist(Exception):
    """Сотрудник не найден"""
    pass


class EmployeeAlreadyExist(Exception):
    """Сотрудник уже существует, добавить нельзя"""
    pass


class PhoneAlreadyTaken(Exception):
    """Телефон занят другим юзером"""
    pass


class DatabaseError(Exception):
    "Проблема в Базе битрикса. Например, дупликаты данных"
    pass


class ConnectorBitrix:
    """Класс для передачи данных регистрации пользователей в Битрикс"""

    _instance = None
    _session: aiohttp.ClientSession = None
    _webhook: str = None

    # Название полей
    PHONE = 'PHONE'
    REF_CODE = 'REF_CODE'
    TG_ID = 'TG_ID'
    ENTRY_DATE = 'ENTRY_DATE'  # Дата первого касания (бот)
    INVITER_VR = 'INVITER_VR'  # Реферальный код приглашающего
    TRAFIC_SOURCE = 'TRAFIC_SOURCE'  # Источник трафика (HR)
    NAME = 'NAME'
    SECOND_NAME = 'SECOND_NAME'
    LAST_NAME = 'LAST_NAME'
    NAME_PARTNER = 'NAME_PARTNER'
    EMAIL = 'EMAIL'
    CITY = 'CITY'
    FORM_NAME = 'FORM_NAME'
    MANAGER_ID = 'MANAGER_ID'
    MANAGER_REF_CODE = 'MANAGER_REF_CODE'
    BANK_NAME = 'BANK_NAME'
    BIK = 'BIK'
    INN = 'INN'
    RSCHET = 'RSCHET'
    BUSINESS = 'BUSINESS'
    OFFER_ACCEPT = 'OFFER_ACCEPT'
    CONF_ACCEPT = 'CONF_ACCEPT'
    # Условия выплаты партнёрского вознаграждения
    PARTNER_PRIZE_ACCEPT = 'PARTNER_PRIZE_ACCEPT'
    PARTNER_TYPE = 'PARTNER_TYPE'

    # Перевод названия полей для лидов (с человеческого на битриксойдный)
    field_lead = {
        TG_ID: 'UF_CRM_TG_ID',
        CITY: 'UF_CRM_CITYPARTNER',
        NAME_PARTNER: 'UF_CRM_NAMEPARTNER',
        FORM_NAME: 'UF_CRM_FORMNAME',
        OFFER_ACCEPT: 'UF_CRM_DOGOVOR',
        CONF_ACCEPT: 'UF_CRM_POLITIKA',
        PARTNER_PRIZE_ACCEPT: 'UF_CRM_1670586101',
        ENTRY_DATE: 'UF_CRM_1670586695',
        INVITER_VR: 'UF_CRM_1670586181',
        TRAFIC_SOURCE: 'UF_CRM_1670586226',
        PARTNER_TYPE: 'uf_crm_promtype',
    }

    # Перевод полей для сделок
    field_deal = {
        REF_CODE: 'UF_CRM_629F76398916A',
        NAME_PARTNER: 'UF_CRM_62A31ED8695D5',
        MANAGER_ID: 'UF_CRM_62B96E88A2A23',
        BANK_NAME: 'UF_CRM_629F7639A4E53',
        BIK: 'UF_CRM_629F7684D91BC',
        INN: 'UF_CRM_629F76399629F',
        RSCHET: 'UF_CRM_629F768500D42',
        NAME: 'UF_CRM_62A31ED8695D5',
        TG_ID: 'UF_CRM_6378DB9ACDFBC',
        CITY: 'UF_CRM_62C80F2307DE2',
        BUSINESS: 'UF_CRM_62A0754067D60',
        OFFER_ACCEPT: 'UF_CRM_629F76E3C1519',
        CONF_ACCEPT: 'UF_CRM_62A1E7A4A3F61',
        PARTNER_PRIZE_ACCEPT: 'UF_CRM_63931F5AB1F1D',
        ENTRY_DATE: 'UF_CRM_63932154A4E50',
        INVITER_VR: 'UF_CRM_63931F5A9327E',
        TRAFIC_SOURCE: 'UF_CRM_63931FB7819D1',
        PARTNER_TYPE: 'UF_CRM_63E0F1ACE29B9',
    }

    # Перевод полей для контакта
    field_contact = {
        REF_CODE: 'UF_CRM_629F763937E2F',
        PHONE: 'PHONE'
    }

    # Перевод полей для менеджера
    field_manager = {
        REF_CODE: 'ufCrm15_1656319502608',
        MANAGER_ID: 'id'
    }

    status_id_for_new_lead = 'NEW'
    title_for_new_lead = '(тест)Новая регистрация в боте'
    title_for_lead_ready_for_use = '(тест)Регистрация партнера'
    formname_for_lead_ready_for_use = 'РЕГИСТРАЦИЯ В РЕФЕРАЛЬНОЙ ПРОГРАММЕ'
    promoter_category_id = '59'
    categoryId = '136'

    # Поля которые указываются на этапе создания лида
    fields_for_lead_registration = [
        CONF_ACCEPT, INVITER_VR, TRAFIC_SOURCE, NAME, SECOND_NAME, LAST_NAME,
        EMAIL, CITY
    ]
    # Поля которые указываются на этапе создания сделки
    fields_for_deal_registration = [
        OFFER_ACCEPT, PARTNER_PRIZE_ACCEPT, MANAGER_REF_CODE, INN, BIK, RSCHET]

    # Поля которые надо вернуть по промоутеру
    fields_for_promoter = [
        REF_CODE, TG_ID, CITY, MANAGER_ID, RSCHET, NAME, SECOND_NAME, 
        LAST_NAME, PARTNER_TYPE]

    # Поля которые надо вернуть по менеджеру
    fields_for_manager = [
        REF_CODE, MANAGER_ID]

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def setup(cls, webhook: str):
        """Возвращает обект класса ConnectorBitrix

        Args:
            webhook (str): URL вебхука Битрикс (он же токен API)
        """
        cls._session = aiohttp.ClientSession()
        cls._webhook = webhook
        cls.bitx = BitrixAsync(
            webhook=cls._webhook,
            verbose=False,
            respect_velocity_policy=True,
            client=cls._session
        )
        logger.info(f'new session for {webhook[:25]}***')

    @classmethod
    async def shutdown(cls) -> bool:
        await cls._session.close()
        logger.info('session closed')

    def __init__(self):
        """Возвращает обект класса ConnectorBitrix"""

    async def _get_fields(self):
        all_fields: list = await self.bitx.get_all(
            'crm.lead.fields'
        )
        return all_fields

    async def _get_lead(
        self,
        ref_code: str = None,
        tg_id: str = None
    ) -> dict:
        """Возвращает Лид

        Args:
            ref_code (str): vr code. Defaults to None.
            tg_id (str): id telegram. Defaults to None.

        Returns:
            dict: словарь поле - значение
        """
        if ref_code:
            filter_field_name = self.field_lead.get('REF_CODE')
            value = ref_code
        elif tg_id:
            filter_field_name = self.field_lead.get('TG_ID')
            value = tg_id
        else:
            raise ValueError('ref_code or tg_id does not have value')

        all_deals: list = await self.bitx.get_all(
            'crm.lead.list',
            params={
                'select': ['*', 'UF_*', 'PHONE', 'EMAIL'],
                'filter': {filter_field_name: value}
            }
        )

        if len(all_deals) == 1:
            return all_deals[0]
        elif len(all_deals) == 0:
            raise EmployeeDoesNotExist
        elif len(all_deals) > 1:
            raise DatabaseError

    async def _get_lead_by_field(
        self,
        field: str,
        value: str
    ) -> dict:

        all_deals: list = await self.bitx.get_all(
            'crm.lead.list',
            params={
                'select': ['*', 'UF_*', 'PHONE', 'EMAIL'],
                'filter': {field: value}
            }
        )

        if len(all_deals) >= 1:
            return all_deals[0]
        elif len(all_deals) == 0:
            raise EmployeeDoesNotExist
        elif len(all_deals) > 1:
            raise DatabaseError

    async def _add_lead(
        self,
        tg_id: str,
        phone: str,
        entry_date: date,
    ):
        tg_field = self.field_lead.get(self.TG_ID)
        date_field = self.field_lead.get(self.ENTRY_DATE)
        result = await self.bitx.call(
            'crm.lead.add',
            {
                'fields': {
                    'TITLE': self.title_for_new_lead,
                    'STATUS_ID': self.status_id_for_new_lead,
                    'PHONE': [{
                        'VALUE': phone,
                        'VALUE_TYPE': 'OTHER'
                    }],
                    tg_field: tg_id,
                    date_field: entry_date,
                }
            }
        )
        return result

    async def _update_lead(self, tg_id: str, field_name: str, value: str):
        lead = await self._get_lead_by_field(
            self.field_lead.get(self.TG_ID), tg_id)
        if field_name == self.PHONE:
            value = [{
                'ID': lead['PHONE'][0]['ID'],
                'VALUE': value
            }]
        elif field_name == self.EMAIL:
            value = [{'VALUE': value}]
        elif field_name in self.field_lead:
            field_name = self.field_lead.get(field_name)
        result = await self.bitx.call(
            'crm.lead.update',
            {
                'id': lead.get('ID'),
                'fields': {
                    field_name: value
                }
            }
        )
        return result

    async def _get_deal(self, field_name: str, value: str) -> dict:
        """_summary_

        Args:
            field_name (str): after translation !
            value (str): _description_

        Returns:
            dict: _description_
        """
        all_deals = await self.bitx.get_all(
            'crm.deal.list',
            params={
                'select': ['*', 'UF_*', 'PHONE'],
                'filter': {field_name: value}
            }
        )
        return all_deals

    async def _get_deal_promoter(
        self,
        ref_code: str = None,
        tg_id: str = None,
        phone: str = None
    ) -> dict:
        """Возвращает сделку по Промоутеру

        Args:
            ref_code (str): vr code. Defaults to None.
            tg_id (str): id telegram. Defaults to None.

        Returns:
            dict: словарь поле - значение
        """
        if ref_code:
            filter_field_name = 'REF_CODE'
            value = ref_code
        elif tg_id:
            filter_field_name = 'TG_ID'
            value = tg_id
        elif phone:
            filter_field_name = 'PHONE'
            value = tg_id
        else:
            raise ValueError('ref_code or tg_id does not have value')

        all_deals = await self.bitx.get_all(
            'crm.deal.list',
            params={
                'select': ['*', 'UF_*'],
                'filter': {self.field_deal.get(filter_field_name): value}
            }
        )

        if len(all_deals) == 1:
            return all_deals[0]
        elif len(all_deals) == 0:
            raise EmployeeDoesNotExist
        elif len(all_deals) > 1:
            raise DatabaseError

    async def _update_deal(self, tg_id: str, field_name: str, value: str):
        deal = await self._get_deal(
            self.field_deal.get(self.TG_ID),
            tg_id
        )
        if field_name == self.MANAGER_ID:
            value = 'T88_' + value

        if field_name in self.field_deal:
            field_name = self.field_deal.get(field_name)

        result = await self.bitx.call(
            'crm.deal.update',
            {
                'id': deal[0].get('ID'),
                'fields': {
                    field_name: value
                }
            }
        )
        return result

    async def _get_contact(self, field_name: str, value: str) -> List[dict]:
        all_contact: list = await self.bitx.get_all(
            'crm.contact.list',
            params={
                'select': ['*', 'UF_*', 'PHONE'],
                'filter': {field_name: value}
            }
        )
        return all_contact

    async def _update_contact(
        self,
        contact_id: str,
        field_name: str,
        value: str
    ):
        contacts = await self._get_contact('ID', contact_id)
        contact = contacts[0]
        if field_name == self.PHONE:
            value = [{
                'ID': contact['PHONE'][0]['ID'],
                'VALUE': value
            }]
        result = await self.bitx.call(
            'crm.lead.update',
            {
                'id': contact.get('ID'),
                'fields': {
                    field_name: value
                }
            }
        )
        return result

    async def _get_promoter_by_phone(self, phone: str) -> dict:
        contacts = await self._get_contact(self.PHONE, phone)
        all_deals = []
        for contact in contacts:
            deal = await self._get_deal(
                field_name='CONTACT_ID',
                value=contact.get('ID')
            )
            if deal[0].get('CATEGORY_ID') == self.promoter_category_id:
                all_deals.append(deal[0])
        if len(all_deals) == 1:
            return all_deals[0]
        elif len(all_deals) == 0:
            raise EmployeeDoesNotExist
        elif len(all_deals) > 1:
            raise DatabaseError

    async def _update_tg_id(self, deal_id: str, tg_id: str) -> bool:
        """Обновить поле tg_id у промоутра

        Args:
            deal_id (str): _description_
            tg_id (str): telegram id, None - если нужно стереть

        Returns:
            bool: _description_
        """
        if tg_id:
            raw = False
        else:
            raw = True
        result = await self.bitx.call(
            'crm.deal.update',
            {
                'id': deal_id,
                'fields': {
                    self.field_deal.get('TG_ID'): tg_id
                }
            },
            raw=raw
        )
        return result

    async def _get_manager(self, ref_code: str) -> str:
        field_name = self.field_manager.get(self.REF_CODE)
        all_deals = await self.bitx.get_all(
            'crm.item.list',
            params={
                'entityTypeId': 136,
                'select': ['*', 'id'],
                'filter': {
                    field_name: ref_code}
            }
        )
        if len(all_deals) == 1:
            manager: int = all_deals[0]
            return manager
        elif len(all_deals) == 0:
            raise EmployeeDoesNotExist
        elif len(all_deals) > 1:
            raise DatabaseError
    
    async def update_tg_id_by_phone(self, phone: str, tg_id: str, ) -> dict:
        """Обновить поле tg_id у промоутра. С проверками

        Args:
            deal_id (str): _description_
            tg_id (str): telegram id, None - если нужно стереть
        """
        promoter = await self._get_promoter_by_phone(phone)

        tg_id_from_contact = promoter.get(self.field_deal.get('TG_ID'))
        if tg_id_from_contact:
            if tg_id_from_contact == tg_id:
                logger.warning(
                    f'EmployeeAlreadyExist tg={tg_id} phone={phone}')
                raise EmployeeAlreadyExist
            else:
                raise PhoneAlreadyTaken

        await self._update_tg_id(
            deal_id=promoter.get('ID'),
            tg_id=tg_id
        )
        
        return promoter


    async def add_promoter(
        self,
        tg_id: str,
        phone: str,
        entry_date: date,
        inviter_vr: str = None,
        link_name: str = None,
    ):
        """Отправить новый номер телефона и тг,
        чтобы создать нового лида промоутера

        Args:
            tg_id (str): id telegram
            phone (str): телефон
            entry_date: дата первого входа в бота,
            inviter_vr: REF_CODE приглашающего,
            link_name: имя диплинка по которму зашел юзер (источник трафика),

        Raises:
            EmployeeAlreadyExist: Уже есть промоутер с таким номером и айди
            PhoneAlreadyTaken: Номер занят другим промоутером

        Returns:
            None: Успешно создан
        """
        logger.info(f'tg={tg_id} phone={phone}')
        try:
            promoter = await self.update_tg_id_by_phone(phone, tg_id)
            #if socssesfuly -> promoter already exists
        except EmployeeDoesNotExist:
            promoter = None

        if promoter:
            raise EmployeeAlreadyExist
                
        try:
            promoter_lead = await self._get_lead(tg_id=tg_id)
        except EmployeeDoesNotExist:
            promoter_lead = None

        if promoter_lead:
            await self._update_lead(
                tg_id=tg_id,
                field_name=self.PHONE,
                value=phone
            )
            await self._update_lead(
                tg_id=tg_id,
                field_name=self.ENTRY_DATE,
                value=entry_date
            )
        else:
            await self._add_lead(tg_id, phone, entry_date)

        if inviter_vr:
            await self.update_promoter(
                tg_id=tg_id,
                field_name=self.INVITER_VR,
                value=inviter_vr
            )

        if link_name:
            await self.update_promoter(
                tg_id=tg_id,
                field_name=self.TRAFIC_SOURCE,
                value=link_name
            )
        return None

    async def update_promoter(
        self,
        tg_id: str,
        field_name: str,
        value: str
    ):
        """Для обновления полей

        Args:
            field_name (str): название поля
            value (str): значение

        Raises:
            ValueError: Поля с таким названием нет
        """
        logger.info(f'tg={tg_id} {field_name}={value}')
        if field_name in self.fields_for_lead_registration:
            await self._update_lead(tg_id, field_name, value)
        elif field_name in self.fields_for_deal_registration:
            if field_name == self.MANAGER_REF_CODE:
                manager = await self._get_manager(ref_code=value)
                await self._update_deal(
                    tg_id=tg_id,
                    field_name=self.MANAGER_ID,
                    value=str(manager['id']))
            else:
                await self._update_deal(tg_id, field_name, value)
        else:
            raise ValueError('wrong field_name')

    async def ready_for_approve(self, tg_id: str):
        """Готов к проверке. Вызвать после завершения первого этапа регистрации

        Args:
            tg_id (str): _description_
        """
        # указываем битриксу что закончили заполнять
        await self._update_lead(
                    tg_id=tg_id,
                    field_name=self.FORM_NAME,
                    value=self.formname_for_lead_ready_for_use)

    async def get_promoter(
            self, tg_id: str = None, ref_code: str = None) -> dict:
        """
        Returns:
            dict: {
                'REF_CODE': 'vr0000',
                'TG_ID': str,
                'CITY': str,
                'MANAGER_ID': str,
                'RSCHET': str,
            }

            EmployeeDoesNotExist
            DatabaseError
        """
        dict_deal = await self._get_deal_promoter(
            tg_id=tg_id,
            ref_code=ref_code
        )
        promoter = {}
        for field in self.fields_for_promoter:
            promoter[field] = dict_deal.get(self.field_deal.get(field))

        # проверка что все поля заполнены = стажер стал промоутером
        if not promoter[self.RSCHET]:
            raise EmployeeDoesNotExist

        contact_id = dict_deal.get('CONTACT_ID')
        contacts = await self._get_contact('ID', contact_id)
        contact = contacts[0]
        promoter[self.LAST_NAME] = contact.get(self.LAST_NAME)
        promoter[self.NAME] = contact.get(self.NAME)
        promoter[self.SECOND_NAME] = contact.get(self.SECOND_NAME)

        return promoter

    async def get_manager(
            self, tg_id: str = None, ref_code: str = None) -> dict:
        """
        Returns:
            dict: {
                'REF_CODE': 'vr0000',
            }
            None - менеджера нет
        """
        if not ref_code:
            promoter_deal = await self.get_promoter(tg_id=tg_id)
            ref_code = promoter_deal.get(self.REF_CODE)
        dict_deal = await self._get_manager(ref_code)
        manager = {}
        for field in self.fields_for_manager:
            manager[field] = dict_deal.get(self.field_manager.get(field))

        return manager

    async def get_promoters_by_manager(self, manager_id) -> List[dict]:
        list_deals = await self._get_deal(
            field_name=self.field_deal.get(self.MANAGER_ID),
            value=manager_id
        )
        list_promoters: List[dict] = []
        for dict_deal in list_deals:
            promoter = {}
            for field in self.fields_for_promoter:
                promoter[field] = dict_deal.get(self.field_deal.get(field))
            list_promoters.append(promoter)

        return list_promoters


async def example():
    webhook_b = 'https://int-active.bitrix24.ru/rest/193/i3qfdc3z8jygp5pp/'
    await ConnectorBitrix.setup(webhook_b)
    cn = ConnectorBitrix()

    tg_id = '1111'
    inviter_promoter_dict = await cn.get_promoter(tg_id='98244574')
    await cn.get_manager(ref_code='vr33909')
    await cn.add_promoter(
        tg_id=tg_id,
        phone='+777777888',
        entry_date=date(2022, 12, 12),
        inviter_vr=inviter_promoter_dict.get(cn.REF_CODE),
        link_name='Тест трафик hr'
        )

    await cn.update_promoter(tg_id, cn.CONF_ACCEPT, 'yes')  # Политика
    await cn.update_promoter(tg_id, cn.NAME, 'Макс')
    await cn.update_promoter(tg_id, cn.SECOND_NAME, 'Максимович')
    await cn.update_promoter(tg_id, cn.LAST_NAME, 'Максов')
    await cn.update_promoter(tg_id, cn.EMAIL, 'lermanma@gmail.com')
    await cn.update_promoter(tg_id, cn.CITY, 'Санкт-Петербург')

    await cn.ready_for_approve(tg_id)  # Когда закончили первую часть реги

    await cn.update_promoter(tg_id, cn.OFFER_ACCEPT, 'yes')  # Договор оферт
    await cn.update_promoter(tg_id, cn.PARTNER_PRIZE_ACCEPT, 'yes')  # Условия выплат
    await cn.update_promoter(tg_id, cn.MANAGER_REF_CODE, 'vr11111')
    await cn.update_promoter(tg_id, cn.BIK, '999999999')
    await cn.update_promoter(tg_id, cn.INN, '120000000000')
    await cn.update_promoter(tg_id, cn.RSCHET, '20000000000000000000')

    await ConnectorBitrix.shutdown()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example())
