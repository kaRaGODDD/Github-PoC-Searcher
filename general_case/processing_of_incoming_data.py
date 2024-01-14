import asyncio
import os

from working_with_API import return_data_from_query

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