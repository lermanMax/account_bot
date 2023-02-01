from datetime import date, datetime
from time import sleep
from loguru import logger
from pygsheets import authorize, Worksheet


class CityDoesNotExist(Exception):
    """Город не найден"""
    pass


class DateDoesNotExist(Exception):
    """Дата не найдена"""
    pass


class PlanSheet():

    _instance = None

    PLAN_WORKSHEET = 'План менеджеры по дням(tech)'

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def is_url_correct(cls, gs_url: str, gs_service_file: str) -> bool:
        try:
            client = authorize(service_file=gs_service_file)
            client.open_by_url(gs_url)
            return True
        except Exception as e:
            logger.error(f'{e}')
            return False

    def setup(cls, gs_url: str, gs_service_file: str):
        cls.gs_link = gs_url
        cls.client = authorize(service_file=gs_service_file)
        cls.sheet = cls.client.open_by_url(cls.gs_link)
        logger.info(f'connect to sheet {cls.sheet.title}')

    def get_title(self) -> str:
        return self.sheet.title

    def get_worksheet(self, ws_name: str) -> Worksheet:
        worksheet = self.sheet.worksheet_by_title(ws_name)
        return worksheet

    def get_cell(self, name):
        worksheet = self.get_worksheet(self.PLAN_WORKSHEET)
        return worksheet.get_row(1)

    def date_form(self, _date: date) -> str:
        return f'{_date:%d/%m/%Y}'

    def get_manager_plan(
            self,
            city_name: str,
            start_date: date,
            end_date: date
    ) -> list:
        worksheet = self.get_worksheet(self.PLAN_WORKSHEET)

        city_cell = worksheet.find(
            pattern=city_name,
            matchEntireCell=True,
            rows=(1, 1)
        )
        if city_cell:
            city_cell = city_cell[0]
        else:
            raise CityDoesNotExist(city_name)
        start_date_cell = worksheet.find(
            pattern=self.date_form(start_date),
            matchEntireCell=True,
            cols=(1, 1)
        )
        end_date_cell = worksheet.find(
            pattern=self.date_form(end_date),
            matchEntireCell=True,
            cols=(1, 1)
        )
        if start_date_cell or end_date_cell:
            start_date_cell = start_date_cell[0]
            end_date_cell = end_date_cell[0]
        else:
            raise DateDoesNotExist
        matrix = worksheet.get_values(
            start=(start_date_cell.row, city_cell.col),
            end=(end_date_cell.row, city_cell.col),
        )
        result = [float(row[0].replace(',', '.')) for row in matrix]
        return result
