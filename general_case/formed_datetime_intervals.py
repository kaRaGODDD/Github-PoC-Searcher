import datetime
from dateutil.relativedelta import relativedelta

async def convert_datetime_object_to_ISO_8601(datetime_object: str):
    '''
    Converts a datetime object to ISO 8601 standard.

    Parameters:
        - datetime_object: The string object to be converted.

    Returns:
        str: The ISO 8601 formatted string representation of the input datetime.
    '''
    return datetime.datetime.strptime(datetime_object, '%Y-%m-%d%H:%M:%S').isoformat() + "Z"

async def generate_intervals(first_year: int, second_year: int):
    '''
    Generates a list of tuples, each tuple representing the start and end date for each month between the specified years.

    Parameters:
        - first_year (int): The starting year.
        - second_year (int): The ending year.

    Returns:
        list: A list of tuples containing start and end dates for each month.
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

async def from_one_interval_to_second_scrapping(first_interval: str, second_interval: str, flag: bool = False):
    '''
    Splits intervals into months if the number of repositories for the given queries is greater than 1000.
    Splitting is done by months for the given interval.

    Parameters:
        - first_interval (str): The start date of the interval.
        - second_interval (str): The end date of the interval.
        - flag (bool): Flag indicating whether to split by months (default is False).

    Returns:
        list or tuple: A list of tuples containing start and end dates for each month, or the original interval.
    '''
    try:
        first_datetime_object = datetime.datetime.strptime(first_interval,"%Y-%m-%d")
        second_datetime_object = datetime.datetime.strptime(second_interval,"%Y-%m-%d")

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

async def year_month_fixed_iterate_day_by_day(first_interval: str,second_interval: str, how_many_days: int = 1):
    '''
    Takes two string objects that fix the same year and month, but the function generates intervals through days.

    Parameters:
        - first_interval (str): The start date of the interval.
        - second_interval (str): The end date of the interval.

    Returns:
        list: A list of tuples containing start and end dates for each day between the specified intervals.
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
        next_day = min(current_date + relativedelta(days=how_many_days),end_date)
        intervals.append((current_date.strftime("%Y-%m-%d"), next_day.strftime("%Y-%m-%d")))
        current_date = next_day
        
    return intervals

async def transform_list_of_intervals(intervals: list):
    new_list_of_intervals = []
    return new_list_of_intervals