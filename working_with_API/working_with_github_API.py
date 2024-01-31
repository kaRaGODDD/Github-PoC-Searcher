import aiohttp
from math import ceil

async def how_many_pages_by_query(url: str, per_search: int) -> int:
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
            count = data.get("total_count",0)
    return ceil(count / per_search)

async def return_data_from_query(url: str, headers: dict, page: int = 0, per_page: int = 30) -> dict:
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
