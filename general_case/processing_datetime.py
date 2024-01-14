import datetime
from returning_values import return_last_date_scrapping
from formed_datetime_intervals import convert_datetime_object_to_ISO_8601


async def formed_datetime_intervals_for_last_scrapping():
    '''
    Async function that forms datetime intervals for the last scrapping session.

    Returns:
        tuple: A tuple containing two ISO 8601 formatted strings representing the last scrapping date and the current date.
    '''
    last_date_scrapping = await return_last_date_scrapping()
    last_date_scrapping = await convert_datetime_object_to_ISO_8601(last_date_scrapping)
    date_now = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
    date_now = await convert_datetime_object_to_ISO_8601(date_now)
    return (last_date_scrapping,date_now)


async def return_datetime_object_in_right_view(datetime_string: str,date_format: str = "%Y-%m-%d"):
    '''
    Async function that converts a datetime string to a datetime object with the specified format.

    Parameters:
        - datetime_string (str): The datetime string to be converted.
        - date_format (str): The format of the datetime string (default is "%Y-%m-%d").

    Returns:
        datetime.datetime: The datetime object.
    '''
    return datetime.datetime.strptime(datetime_string,date_format)

async def calculate_difference_between_two_dates(first_date: str, second_date: str):
    '''
    Async function that calculates the difference in days between two ISO 8601 formatted datetime strings.

    Parameters:
        - first_date (str): The first ISO 8601 formatted datetime string.
        - second_date (str): The second ISO 8601 formatted datetime string.

    Returns:
        int: The absolute difference in days.
    '''
    first_datetime = await return_datetime_object_in_right_view(first_date,"%Y-%m-%dT%H:%M:%SZ")
    second_datetime = await return_datetime_object_in_right_view(second_date,"%Y-%m-%dT%H:%M:%SZ")
    return abs((first_datetime - second_datetime).days)

async def to_strftime_format(last_date_scrapping: str, date_now: str,format: str = "%Y-%m-%dT%H:%M:%SZ"):
    '''
    Asynchronous function that converts ISO 8601 formatted datetime strings to custom format.

    Parameters:
        - last_date_scrapping (str): The ISO 8601 formatted datetime string representing the last scrapping date.
        - date_now (str): The ISO 8601 formatted datetime string representing the current date.
        - format (str): The format of the input datetime strings (default is "%Y-%m-%dT%H:%M:%SZ").

    Returns:
        tuple: A tuple containing two strings in "%Y-%m-%d" format representing the last scrapping date and the current date.
    '''
    first_interval = await return_datetime_object_in_right_view(last_date_scrapping,format)
    first_interval = first_interval.strftime("%Y-%m-%d")
    second_interval = await return_datetime_object_in_right_view(date_now,format)
    second_interval = second_interval.strftime("%Y-%m-%d")
    return (first_interval,second_interval)
