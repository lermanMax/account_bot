from __future__ import annotations

from datetime import datetime, timedelta
from calendar import WEDNESDAY


class WorkWeekMixin:
    first_work_week_day = WEDNESDAY

    @classmethod
    def get_first_day_of_week(cls) -> datetime:
        today = datetime.today()
        offset = (today.weekday() - cls.first_work_week_day) % 7
        date_firs_day = today - timedelta(days=offset)
        return date_firs_day

    @classmethod
    def get_today(cls) -> datetime:
        today = datetime.today()
        return today
