import asyncio
import aiohttp
import datetime
import subprocess
import time
import os

from formed_datetime_intervals import *
from write_last_date import write_last_date_scrapping
from create_directories import create_data_directory, create_directory_on_pc
from dotenv import load_dotenv, set_key
from enum import Enum, auto
from math import ceil

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

class Languages(Enum):
    PYTHON = auto()
    GO = auto()
    JavaScript = auto()

async def return_token():
    return os.getenv("GITHUB_TOKEN")

async def return_url():
    return "https://api.github.com/search/repositories?q=proof%20of%20concept%20created:{}..{}"

async def return_last_date_scrapping():
    return os.getenv("LAST_DATE_SCRAPPING")

async def how_many_pages_need_to_parse(url: str, per_search: int):
    '''
    Async function that retrieves information from a given URL representing a search query
    and calculates the number of pages needed to parse all the repositories based on the specified items per search.

    Parameters:
        - url (str): The URL representing a search query.
        - per_search (int): The number of repositories/items to be retrieved per search.

    Returns:
        int: The calculated number of pages needed to parse all the repositories.
    '''
    if per_search > 100:
        raise Exception("Per search parameter cannot be greater than 100")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            count = data["total_count"]
    return ceil(count / per_search)

async def clone_repository(repository_url: str, repository_name: str,name_of_the_interval_directory: str):
    '''
    Async function that clones a repository based on its URL. If the repository is already cloned on the PC, it performs a git pull.

    Parameters:
        - repository_url (str): The URL of the repository to be cloned.
        - repository_name (str): The name of the repository.
        - name_of_the_interval_directory (str) The name of interval directory.

    Raises:
        Exception: If an error occurs during the cloning process.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    path_to_data_directory = os.path.join(os.getenv("PATH_TO_THE_DATA_DIRECTORY"),name_of_the_interval_directory)
    path_to_repository = os.path.join(path_to_data_directory, repository_name)
    try:
        exists = await asyncio.to_thread(os.path.exists, path_to_repository)
        if exists:
            await asyncio.to_thread(os.chdir,os.path.join(path_to_repository))
            process = await asyncio.create_subprocess_exec("git","pull")
            await process.wait()
        else:
            process = await asyncio.create_subprocess_exec("git", "clone", "--depth", "1", repository_url, path_to_repository)
            await process.wait()
    except Exception as e:
        print(f"Error cloning repository {repository_url}: {e}")

async def return_data_from_query(url: str, page: int,headers: dict, per_page: int):
    '''
    Async function that retrieves data from a query URL with pagination parameters.

    Parameters:
        - url (str): The base URL for the query.
        - page (int): The page number for pagination.
        - headers (dict): Headers to be included in the HTTP request.
        - per_page (int): Number of items per page.

    Returns:
        dict: JSON data retrieved from the query.
    '''
    async with aiohttp.ClientSession() as session:
        async with session.get(url + f"&page={page}&per_page={per_page}", headers=headers) as response:
            data = await response.json()
    return data    

async def process_page(url: str, page: int,headers: dict, per_page: int,name_of_the_interval_directory: str):
    '''
    Async function that processes a page of data, cloning repositories using the `clone_repository` function.

    Parameters:
        - url (str): The base URL for the query.
        - page (int): The page number for pagination.
        - headers (dict): Headers to be included in the HTTP request.
        - per_page (int): Number of items per page.
        - name_of_the_interval_directory (str) The name of interval directory.
    '''
    data = await return_data_from_query(url,page,headers,per_page)
    for item in data["items"]:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(clone_repository(item["clone_url"],item["name"],name_of_the_interval_directory))

async def get_users_and_their_repositories(intervals: tuple, token: str,headers: dict,per_page: int,name_of_the_interval_directory: str):
    '''
    Async function that iterates over specified intervals, retrieves user repositories, and clones them.

    Parameters:
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - intervals (tuple): Tuple of date intervals.
        - token (str): Authorization token for API requests.
        - headers (dict): Headers to be included in the HTTP request.
        - per_page (int): Number of items per page.
        - name_of_the_interval_directory (str) The name of interval directory.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    await asyncio.to_thread(os.chdir, os.getenv("PATH_TO_THE_DATA_DIRECTORY"))
    for i in range(0, len(intervals)):
        since, until = intervals[i]
        formatted_url = await return_url()
        formatted_url = formatted_url.format(since, until)
        pages_on_query = await how_many_pages_need_to_parse(formatted_url,30)
        tasks = [process_page(formatted_url, j,headers,per_page,name_of_the_interval_directory) for j in range(0,pages_on_query + 1)]
        await asyncio.gather(*tasks)

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

async def determine_interval_type(difference):
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

async def most_popular_repositories(special_url_for_scrapping_pages):
    pass

async def main():
    token = await return_token()
    url_for_scrapping_pages = await return_url()
    headers = {"Authorization": f"Bearer {token}"}
    await create_data_directory()
    choice = ParsingChoice.SINCE_LAST_SCRAPPING
    match choice:
        case ParsingChoice.YEAR_BY_YEAR:
            first_interval = "2015-01-01"
            second_interval = "2016-01-01"
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval,second_interval)
            await сloning_is_carried_out_by_year(url_for_scrapping_pages,headers,token,2015,2016,name_of_the_interval_directory)
        case ParsingChoice.FROM_ONE_INTERVAL_TO_SECOND:
            first_interval = "2015-03-05"
            second_interval = "2015-04-07"
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval,second_interval)
            await сloning_is_performed_at_specified_intervals(url_for_scrapping_pages,headers,token,first_interval,second_interval,name_of_the_interval_directory)
        case ParsingChoice.YEAR_AND_MONTH_FIXED:
            first_interval = "2015-03-01"
            second_interval = "2015-03-05"
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval,second_interval)
            await cloning_is_performed_according_to_a_fixed_year_and_month(url_for_scrapping_pages,headers,token,first_interval,second_interval,name_of_the_interval_directory)
        case ParsingChoice.SINCE_LAST_SCRAPPING:
            first_interval = os.getenv("LAST_DATE_SCRAPPING")
            second_interval = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
            first_interval_strftime_format,second_interval_strftime_format = await to_strftime_format(first_interval,second_interval,"%Y-%m-%d%H:%M:%S")
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval_strftime_format,second_interval_strftime_format)
            await since_last_scrapping(url_for_scrapping_pages,headers,token,False,name_of_the_interval_directory)
        case ParsingChoice.MOST_POPULAR:
            pass
        case _:
            print("Doesnt know that option")
    

if __name__ == "__main__":
    asyncio.run(main())
    