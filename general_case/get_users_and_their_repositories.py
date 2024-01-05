import subprocess
import asyncio
import aiohttp
import os
import time
import datetime

from dotenv import load_dotenv
from formed_datetime_intervals import generate_intervals
from math import ceil
from create_directories import create_data_directory

load_dotenv()

async def how_many_pages_need_to_parse(url: str):
    PER_SEARCH = 30
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            count = data["total_count"]
    return ceil(count / PER_SEARCH)

async def clone_repository(repository_url: str, repository_name: str):
    path_to_data_directory = os.getenv("PATH_TO_THE_DATA_DIRECTORY")
    path_to_repository = os.path.join(path_to_data_directory, repository_name)
    try:
        exists = await asyncio.to_thread(os.path.exists, path_to_repository)
        if exists:
            print(f"Repository {repository_name} already clonned")
        else:
            process = await asyncio.create_subprocess_exec("git", "clone", "--depth", "1", repository_url, path_to_repository)
            await process.wait()
    except Exception as e:
        print(f"Error cloning repository {repository_url}: {e}")

async def process_page(url: str, page: int,headers: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(url + f"&page={page}&per_page={30}", headers=headers) as response:
            data = await response.json()
            print(data)
            for item in data["items"]:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(clone_repository(item["clone_url"],item["name"]))

async def get_users_and_their_repositories():
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    first_year_for_scrapping = datetime.datetime(2015,1,1).strftime("%Y-%m-%d")
    second_year_for_scrapping = datetime.datetime(2015,12,31).strftime("%Y-%m-%d")
    url_for_scrapping_pages = os.getenv('URL') 
    url_for_scrapping_pages = url_for_scrapping_pages.format(first_year_for_scrapping,second_year_for_scrapping) 
    pages = await how_many_pages_need_to_parse(url_for_scrapping_pages)
    intervals = await generate_intervals(2015, 2016)
    await asyncio.to_thread(os.chdir, os.getenv("PATH_TO_THE_DATA_DIRECTORY"))
    for i in range(0, pages + 1):
        since, until = intervals[i]
        formatted_url = await asyncio.to_thread(os.getenv, "URL")
        formatted_url = formatted_url.format(since, until)
        pages = await how_many_pages_need_to_parse(formatted_url)
        tasks = [process_page(formatted_url, j,headers) for j in range(0,pages+1)]
        await asyncio.gather(*tasks)
        print(f"page#{i} done")
        # async with asyncio.TaskGroup() as tg:
        #     tg.create_task(process_page(formatted_url,i,headers))
        
async def main():
    await create_data_directory()
    await get_users_and_their_repositories()

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)