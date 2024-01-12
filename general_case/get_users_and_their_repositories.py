import asyncio
import aiohttp
import datetime
import subprocess
import time
import os

from formed_datetime_intervals import *
from write_last_date import write_last_date_scrapping
from create_directories import create_data_directory
from dotenv import load_dotenv, set_key
from enum import Enum, auto
from math import ceil

load_dotenv()

class ParsingChoice(Enum):
    YEAR_BY_YEAR = auto()
    FROM_ONE_INTERVAL_TO_SECOND = auto()
    YEAR_AND_MONTH_FIXED = auto()

class Languages(Enum):
    PYTHON = auto()
    GO = auto()
    JavaScript = auto()

async def return_token():
    return os.getenv("GITHUB_TOKEN")

async def return_url():
    return os.getenv("URL")

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

async def clone_repository(repository_url: str, repository_name: str):
    '''
    Async function that clones a repository based on its URL. If the repository is already cloned on the PC, it performs a git pull.

    Parameters:
        - repository_url (str): The URL of the repository to be cloned.
        - repository_name (str): The name of the repository.

    Raises:
        Exception: If an error occurs during the cloning process.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    path_to_data_directory = os.getenv("PATH_TO_THE_DATA_DIRECTORY")
    path_to_repository = os.path.join(path_to_data_directory, repository_name)
    try:
        exists = await asyncio.to_thread(os.path.exists, path_to_repository)
        if exists:
            process = await asyncio.create_subprocess_exec("git","pull",repository_url)
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

async def process_page(url: str, page: int,headers: dict, per_page: int):
    '''
    Async function that processes a page of data, cloning repositories using the `clone_repository` function.

    Parameters:
        - url (str): The base URL for the query.
        - page (int): The page number for pagination.
        - headers (dict): Headers to be included in the HTTP request.
        - per_page (int): Number of items per page.
    '''
    data = await return_data_from_query(url,page,headers,per_page)
    for item in data["items"]:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(clone_repository(item["clone_url"],item["name"]))

async def get_users_and_their_repositories(url_for_scrapping_pages: str,intervals: tuple, token: str,headers: dict,per_page: int):
    '''
    Async function that iterates over specified intervals, retrieves user repositories, and clones them.

    Parameters:
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - intervals (tuple): Tuple of date intervals.
        - token (str): Authorization token for API requests.
        - headers (dict): Headers to be included in the HTTP request.
        - per_page (int): Number of items per page.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    await asyncio.to_thread(os.chdir, os.getenv("PATH_TO_THE_DATA_DIRECTORY"))
    for i in range(0, len(intervals) + 1):
        since, until = intervals[i]
        formatted_url = await asyncio.to_thread(os.getenv, "URL")
        formatted_url = formatted_url.format(since, until)
        pages_on_query = await how_many_pages_need_to_parse(formatted_url,30)
        tasks = [process_page(formatted_url, j,headers,per_page) for j in range(0,pages_on_query + 1)]
        await asyncio.gather(*tasks)

async def сloning_is_carried_out_by_year(headers: dict, url_for_scrapping_pages: str, token: str,first_year: int, second_year: int):
    '''
    Async function that performs cloning based on specified year intervals.

    Parameters:
        - headers (dict): Headers to be included in the HTTP request.
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - token (str): Authorization token for API requests.
        - first_year (int): The starting year for the interval.
        - second_year (int): The ending year for the interval.

    Raises:
        Exception: If either the first or second year is greater than 2024.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    if first_year > 2024 or second_year > 2024:
        raise Exception("First year and second year cannot be greater than 2024") 
    first_date = datetime.datetime(first_year,1,1).strftime("%Y-%m-%d")
    second_date = datetime.datetime(second_year,1,1).strftime("%Y-%m-%d")
    url_for_scrapping_pages = url_for_scrapping_pages.format(first_date,second_date)
    intervals = await generate_intervals(first_year,second_year)
    await get_users_and_their_repositories(url_for_scrapping_pages,intervals,token,headers,30)

async def сloning_is_performed_at_specified_intervals(url_for_scrapping_pages: str,headers: dict,token: str, first_interval: str, second_interval: str):
    '''
    Async function that performs cloning based on specified date intervals.

    Parameters:
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - headers (dict): Headers to be included in the HTTP request.
        - token (str): Authorization token for API requests.
        - first_interval (str): The starting date interval.
        - second_interval (str): The ending date interval.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    intervals = await from_one_interval_to_second_scrapping(first_interval,second_interval,True)
    url_for_scrapping_pages = url_for_scrapping_pages.format(first_interval,second_interval)
    await get_users_and_their_repositories(url_for_scrapping_pages,intervals,token,headers,30)

async def cloning_is_performed_according_to_a_fixed_year_and_month(url_for_scrapping_pages: str,headers: dict, token: str, first_interval: str, second_interval: str):
    '''
    Async function that performs cloning based on fixed year and month intervals.

    Parameters:
        - url_for_scrapping_pages (str): The base URL for scrapping pages.
        - headers (dict): Headers to be included in the HTTP request.
        - token (str): Authorization token for API requests.
        - first_interval (str): The starting date interval.
        - second_interval (str): The ending date interval.

    Note:
        This function assumes that the environment variable "PATH_TO_THE_DATA_DIRECTORY" is set.
    '''
    intervals = await year_month_fixed_iterate_day_by_day(first_interval,second_interval,True)
    url_for_scrapping_pages = url_for_scrapping_pages.format(first_interval,second_interval)
    await get_users_and_their_repositories(url_for_scrapping_pages,intervals,token,headers,30)

async def main():
    token = await return_token()
    url_for_scrapping_pages = await return_url()
    headers = {"Authorization": f"Bearer {token}"}
    await create_data_directory()
    choice = ParsingChoice.FROM_ONE_INTERVAL_TO_SECOND
    match choice:
        case ParsingChoice.YEAR_BY_YEAR:
            await сloning_is_carried_out_by_year(headers,url_for_scrapping_pages,token,2015,2016)
        case ParsingChoice.FROM_ONE_INTERVAL_TO_SECOND:
            await сloning_is_performed_at_specified_intervals(url_for_scrapping_pages,headers,token,"2015-03-05","2015-04-07")
        case ParsingChoice.YEAR_AND_MONTH_FIXED:
            await cloning_is_performed_according_to_a_fixed_year_and_month(url_for_scrapping_pages,headers,token)
        case _:
            print("Doesnt know that option")
    

if __name__ == "__main__":
    asyncio.run(main())
    