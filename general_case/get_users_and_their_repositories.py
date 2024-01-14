import asyncio

from processing_of_incoming_data import process_page
from returning_values import return_url
from working_with_API import how_many_pages_need_to_parse

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
    for i in range(0, len(intervals)):
        since, until = intervals[i]
        formatted_url = await return_url()
        formatted_url = formatted_url.format(since, until)
        pages_on_query = await how_many_pages_need_to_parse(formatted_url,30)
        tasks = [process_page(formatted_url, j,headers,per_page,name_of_the_interval_directory) for j in range(0,pages_on_query + 1)]
        await asyncio.gather(*tasks)
