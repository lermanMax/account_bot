from __future__ import annotations
from typing import Tuple

from datetime import datetime, timedelta, date
from calendar import MONDAY


class WorkWeekMixin:
    first_work_week_day = MONDAY

    @classmethod
    def get_first_day_of_week(cls) -> datetime:
        today = datetime.today()
        offset = (today.weekday() - cls.first_work_week_day) % 7
        date_firs_day = today - timedelta(days=offset)
        return date_firs_day

    @classmethod
    def get_last_day_of_week(cls) -> datetime:
        date_last_day = cls.get_first_day_of_week() + timedelta(days=7)
        return date_last_day

    @classmethod
    def get_today(cls) -> datetime:
        today = datetime.today()
        return today

    @classmethod
    def _make_week_days(cls, start_date, end_date) -> Tuple[date]:
        delta = end_date - start_date
        week = (
            (start_date+timedelta(days=i)).date()
            for i in range(delta.days + 1)
        )
        return week

    @classmethod
    def get_this_week_days(cls) -> Tuple[date]:
        start_date = cls.get_first_day_of_week()
        end_date = cls.get_today()
        week = cls._make_week_days(start_date, end_date)
        return week

    @classmethod
    def get_last_week_days(cls) -> Tuple[date]:
        first_day = cls.get_first_day_of_week()
        start_date = first_day - timedelta(days=7)
        end_date = first_day - timedelta(days=1)
        week = cls._make_week_days(start_date, end_date)
        return week
