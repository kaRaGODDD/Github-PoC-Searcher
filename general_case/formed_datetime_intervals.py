import datetime
import asyncio

from dateutil.relativedelta import relativedelta

async def convert_datetime_object_to_ISO_8601(object_that_need_to_convert):
    '''
        Function that convert datetime object to ISO 8601 standatrt 
    '''
    return datetime.datetime.strptime(object_that_need_to_convert, '%Y-%m-%d %H:%M:%S').isoformat() + "Z"

async def generate_intervals(first_year : int, second_year : int):
    '''
        Function that generate the list of tuples, each tuple is the date from first year to second year per month
    '''
    intervals = [
        (
            datetime.datetime(year, month, 1).strftime("%Y-%m-%d"),
            datetime.datetime(year, month + 1, 1).strftime("%Y-%m-%d")
        )
        for year in range(first_year, second_year + 1)
        for month in range(1, 12)
        ]
    return intervals

async def from_one_interval_to_second_scrapping(first_interval : str, second_interval : str, flag : bool = False):
    '''
        Function that splits intervals into months, if the number of repositories for the given queries > 1000
        Splitting is done by months, for the given interval
    '''
    try:
        first_datetime_object = datetime.datetime.strptime(first_interval,"%Y-%m-%d")
        second_datetime_object = datetime.datetime.strptime(second_interval,"%Y-%m-%d")

        if first_datetime_object.year != second_datetime_object.year or first_datetime_object.month != second_datetime_object.month:
            raise Exception("Month and year should be the same")

        if first_datetime_object > second_datetime_object:
            raise Exception("First date should be earlier than the second one")
        
    except ValueError:
        print("Invalid date format. Please use 'YYYY-MM-DD'")
        return None
    
    if first_datetime_object > second_datetime_object:
        raise Exception("First date should be earlier than the second one")

    if flag:
        current_date = first_datetime_object
        end_date = second_datetime_object
        intervals = []
        while current_date < end_date:
            next_month = min(current_date + relativedelta(months=1),end_date)
            intervals.append((current_date.strftime("%Y-%m-%d"), next_month.strftime("%Y-%m-%d")))
            current_date = next_month

        return intervals

    return first_interval, second_interval

async def year_month_fixed_iterate_day_by_day(first_interval : str,second_interval : str):
    '''
        Function that takes two string object both of them fix the same year and month, but function generate intervals through day
    '''
    try:
        first_datetime_object = datetime.datetime.strptime(first_interval,"%Y-%m-%d")   
        second_datetime_object = datetime.datetime.strptime(second_interval,"%Y-%m-%d")

        if first_datetime_object.year != second_datetime_object.year or first_datetime_object.month != second_datetime_object.month:
            raise Exception("Month and year should be the same")

        if first_datetime_object > second_datetime_object:
            raise Exception("First date should be earlier than the second one")

    except ValueError:
        print("Invalid date format. Please use 'YYYY-MM-DD'")
        return None
    
    intervals = []
    current_date = first_datetime_object
    end_date = second_datetime_object

    while current_date < end_date:
        next_day = min(current_date + relativedelta(days=1),end_date)
        intervals.append((current_date.strftime("%Y-%m-%d"), next_day.strftime("%Y-%m-%d")))
        current_date = next_day
        

    return intervals
