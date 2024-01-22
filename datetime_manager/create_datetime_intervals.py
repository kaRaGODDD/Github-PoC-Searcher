import os
import datetime 

from constants_and_other_stuff.structs import StringInterval, DatetimeInterval
from dateutil.relativedelta import relativedelta

from typing import List
from dotenv import load_dotenv

load_dotenv()

async def create_intervals(interval: StringInterval) -> List[StringInterval]:
    intervals = await _split_interval_by_parts(interval)
    return intervals

async def _split_interval_by_parts(interval: StringInterval) -> List[StringInterval]:
    new_interval = await _convert_to_datetime_interval(interval)
    current_date, end_date = await _return_components(new_interval)
    dates = []
    while current_date < end_date:
        next_month = min(current_date + relativedelta(months=1),end_date)
        string_interval_object = StringInterval(current_date.strftime("%Y-%m-%d"),next_month.strftime("%Y-%m-%d"))
        dates.append(string_interval_object)
        current_date = next_month
    return dates

async def _convert_to_datetime_interval(interval: StringInterval) -> DatetimeInterval:  
    first_datetime_interval = datetime.datetime.strptime(interval.first_interval,"%Y-%m-%d")
    second_datetime_interval = datetime.datetime.strptime(interval.second_interval,"%Y-%m-%d")
    return DatetimeInterval(first_datetime_interval,second_datetime_interval)

async def _return_components(intervals: DatetimeInterval | StringInterval) -> tuple[str | datetime.datetime, str | datetime.datetime]:
    return (intervals.first_interval, intervals.second_interval)
