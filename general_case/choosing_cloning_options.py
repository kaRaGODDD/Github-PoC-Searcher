import asyncio
import os
from datetime import datetime
from enum import Enum, auto

from dotenv import load_dotenv

from create_directories import create_directory_on_pc
from formed_datetime_intervals import *
from get_users_and_their_repositories import get_users_and_their_repositories
from processing_datetime import *
from write_last_date import write_last_date_scrapping

load_dotenv()

class ParsingChoice(Enum):
    YEAR_BY_YEAR = auto()
    FROM_ONE_INTERVAL_TO_SECOND = auto()
    YEAR_AND_MONTH_FIXED = auto()
    SINCE_LAST_SCRAPPING = auto()
    MOST_POPULAR = auto()

class IntervalType(Enum):
    DAYS = auto()
    WEAKS = auto()
    MONTH = auto()
    YEAR = auto()

async def сloning_is_carried_out_by_year(url_for_scrapping_pages: str, headers: dict, token: str,first_year: int, second_year: int,name_of_the_interval_directory: str):
    '''
    Async function that performs cloning based on specified year intervals.

    Parameters:
        - headers (dict): Headers to be included in the HTTP request.
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - token (str): Authorization token for API requests.
        - first_year (int): The starting year for the interval.
        - second_year (int): The ending year for the interval.
        - name_of_the_interval_directory (str) The name of interval directory.

    Raises:
        Exception: If either the first or second year is greater than 2024.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    if first_year > datetime.datetime.now().year or second_year > datetime.datetime.now().year:
        raise Exception(f"First year or second year cannot be greater than {datetime.datetime.now().year}") 
    first_date = datetime.datetime(first_year,1,1).strftime("%Y-%m-%d")
    second_date = datetime.datetime(second_year,1,1).strftime("%Y-%m-%d")
    url_for_scrapping_pages = url_for_scrapping_pages.format(first_date,second_date)
    intervals = await generate_intervals(first_year,second_year)
    await get_users_and_their_repositories(intervals,token,headers,30,name_of_the_interval_directory)

async def сloning_is_performed_at_specified_intervals(url_for_scrapping_pages: str,headers: dict,token: str, first_interval: str, second_interval: str,name_of_the_interval_directory: str):
    '''
    Async function that performs cloning based on specified date intervals.

    Parameters:
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - headers (dict): Headers to be included in the HTTP request.
        - token (str): Authorization token for API requests.
        - first_interval (str): The starting date interval.
        - second_interval (str): The ending date interval.
        - name_of_the_interval_directory (str) The name of interval directory.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    intervals = await from_one_interval_to_second_scrapping(first_interval,second_interval,True)
    url_for_scrapping_pages = url_for_scrapping_pages.format(first_interval,second_interval)
    await get_users_and_their_repositories(intervals,token,headers,30,name_of_the_interval_directory)

async def cloning_is_performed_according_to_a_fixed_year_and_month(url_for_scrapping_pages: str,headers: dict, token: str, first_interval: str, second_interval: str,name_of_the_interval_directory: str):
    '''
    Async function that performs cloning based on fixed year and month intervals.

    Parameters:
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - headers (dict): Headers to be included in the HTTP request.
        - token (str): Authorization token for API requests.
        - first_interval (str): The starting date interval.
        - second_interval (str): The ending date interval.
        - name_of_the_interval_directory (str) The name of interval directory.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    intervals = await year_month_fixed_iterate_day_by_day(first_interval,second_interval,True)
    url_for_scrapping_pages = url_for_scrapping_pages.format(first_interval,second_interval)
    await get_users_and_their_repositories(intervals,token,headers,30,name_of_the_interval_directory)

async def determine_interval_type(difference: int):
    '''
    Async function that determines the type of time interval based on the difference in days.

    Parameters:
        - difference (int): The difference in days.

    Returns:
        IntervalType: An enumeration representing the type of time interval.
    '''
    if difference <= 7:
        return IntervalType.DAYS
    elif difference < 31:
        return IntervalType.WEAKS
    elif difference <= 365:
        return IntervalType.MONTH
    else:
        return IntervalType.YEAR

async def since_last_scrapping(url_for_scrapping_pages: str,headers: dict, token: str, rewrite_last_date_scrapping: bool,name_of_the_interval_directory: str):
    '''
    Async function that performs scrapping since the last recorded scrapping date.

    Parameters:
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - headers (dict): Headers to be included in the HTTP request.
        - token (str): Authorization token for API requests.
        - rewrite_last_date_scrapping (bool): Flag indicating whether to rewrite the last scrapping date.
        - name_of_the_interval_directory (str) The name of interval directory.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
        If rewrite_last_date_scrapping is True, it updates the last scrapping date.
    '''
    last_date_scrapping, date_now = await formed_datetime_intervals_for_last_scrapping()
    url_for_scrapping_pages = url_for_scrapping_pages.format(last_date_scrapping,date_now)
    difference = await calculate_difference_between_two_dates(last_date_scrapping,date_now)
    type_of_interval = await determine_interval_type(difference) 
    if rewrite_last_date_scrapping:
        await write_last_date_scrapping(datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S"))
    match type_of_interval:
        case IntervalType.YEAR:
            first_interval = datetime.datetime.strptime(last_date_scrapping,"%Y-%m-%d").year
            second_interval = datetime.datetime.strptime(date_now,"%Y-%m-%d").year
            intervals = await generate_intervals(datetime.datetime.strptime(first_interval,second_interval))
        case IntervalType.MONTH:
            first_interval, second_interval = await to_strftime_format(last_date_scrapping,date_now)
            intervals = await from_one_interval_to_second_scrapping(first_interval,second_interval)
        case IntervalType.WEAKS:
            first_interval, second_interval = await to_strftime_format(last_date_scrapping,date_now)
            intervals = await year_month_fixed_iterate_day_by_day(first_interval,second_interval,7)
        case IntervalType.DAYS:
            first_interval, second_interval = await to_strftime_format(last_date_scrapping,date_now)
            intervals = await year_month_fixed_iterate_day_by_day(first_interval,second_interval)
        case _:
            pass
    await get_users_and_their_repositories(intervals,token,headers,30,name_of_the_interval_directory)

async def formed_interval_and_switch_directory(first_interval: str, second_interval: str):
        '''
        Asynchronous function that processes time intervals and switches the current working directory.

        Parameters:
            - directory_path (str): The path of the directory to switch to.
            - last_date_scrapping (str): The ISO 8601 formatted datetime string representing the last scrapping date.
            - date_now (str): The ISO 8601 formatted datetime string representing the current date.
            - format (str): The format of the input datetime strings (default is "%Y-%m-%dT%H:%M:%SZ").

        Returns:
        tuple: A tuple containing two strings in "%Y-%m-%d" format representing the last scrapping date and the current date.
        '''
        name_of_the_interval_directory = "-".join([first_interval, second_interval])
        await create_directory_on_pc(name_of_the_interval_directory)
        path = os.path.join(os.getenv("PATH_TO_THE_DATA_DIRECTORY"),name_of_the_interval_directory)
        await asyncio.to_thread(os.chdir,path)
        return name_of_the_interval_directory