from typing import NamedTuple, List
from loguru import logger
from datetime import datetime
import aiomysql


class SaleEntry(NamedTuple):
    green_id: int
    order_status: str
    count: int
    full_sum: int
    vr_code: str
    sale_time: datetime


class Ticket(NamedTuple):
    green_id: int
    order_status: str
    price: int
    vr_code: str
    sale_time: datetime


class ConnectorSalesBase:
    _instance = None
    pool = None

    # def __new__(cls):
    #     if not isinstance(cls._instance, cls):
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    @classmethod
    async def create_conn(cls, host, port, user, password, db, loop=None):
        cls.host = host
        cls.port = port
        cls.user = user
        cls.password = password
        cls.db = db

        cls.pool = await aiomysql.create_pool(
            host=cls.host, port=cls.port, user=cls.user,
            password=cls.password, db=cls.db, loop=loop)

    @classmethod
    async def close(cls):
        cls.pool.close()
        logger.info('pool closed')

    def __init__(self):
        pass

    async def get_sales_by_promoter(
            self, vr_code: str, start_date, end_date=None) -> List[SaleEntry]:
        """Get sales for a set period of time (start & end date inclusively)
        --by promoter

        Args:
            vr_code (str): _description_
            start_date (_type_): _description_
            end_date (_type_, optional): _description_. Defaults to None.

        Returns:
            List[SaleEntry]:
        """
        logger.info(f'{vr_code} {start_date} {end_date}')
        if end_date is None:
            end_date = start_date

        async with self.pool.acquire() as conn:
            cur = await conn.cursor()

            select_script = '''
                SELECT telegreen_id, order_status, telegreen_total_count,
                telegreen_total_sum, telegreen_sname, telegreen_approved_date
                FROM telegreen_direct_orders
                WHERE CAST(telegreen_approved_date AS date)
                BETWEEN CAST(%s AS date) AND CAST(%s AS date)
                AND telegreen_sname = %s
                AND order_status = 'print';'''

            await cur.execute(select_script, (start_date, end_date, vr_code))
            sale_entries = await cur.fetchall()
            await cur.close()

        return [SaleEntry(*entry) for entry in sale_entries]

    async def get_all_sales(
            self, start_date, end_date=None) -> List[SaleEntry]:
        """Get all sales for a set period of time (start & end date inclusively)

        Args:
            start_date (_type_): _description_
            end_date (_type_, optional): _description_. Defaults to None.

        Returns:
            List[SaleEntry]: _description_
        """
        logger.info(f'{start_date} {end_date}')
        if end_date is None:
            end_date = start_date

        cur = await self.conn.cursor()

        select_script = '''
            SELECT telegreen_id, order_status, telegreen_total_count,
            telegreen_total_sum, telegreen_sname, telegreen_approved_date
            FROM telegreen_direct_orders
            WHERE CAST(telegreen_approved_date AS date)
            BETWEEN CAST(%s AS date) AND CAST(%s AS date)
            AND order_status = 'print';'''

        await cur.execute(select_script, (start_date, end_date))
        sale_entries = await cur.fetchall()
        await cur.close()
        return [SaleEntry(*entry) for entry in sale_entries]
