import subprocess
import asyncio
import aiohttp
import os
import time

from dotenv import load_dotenv
from formed_datetime_intervals import generate_intervals
from math import ceil
from create_directories import create_data_directory

load_dotenv()

async def how_many_pages_need_to_parse(url: str):
    PER_SEARCH = 30
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            count = data["total_count"]
    return ceil(count / PER_SEARCH)

async def clone_repository(repository_url: str):
    try:
        process = await asyncio.create_subprocess_exec("git", "clone", "--depth", "1", repository_url)
        await process.wait()
    except Exception as e:
        print(f"Error cloning repository {repository_url}: {e}")

async def process_page(url: str, page: int):
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url + f"&page={page}&per_page={30}", headers=headers) as response:
            data = await response.json()
            await asyncio.to_thread(os.chdir, os.getenv("PATH_TO_THE_DATA_DIRECTORY"))
            for item in data["items"]:
                await clone_repository(item["clone_url"])

async def get_users_and_their_repositories():
    intervals = await generate_intervals(2015, 2016)
    for i in range (1,3):
        since, until = intervals[i]
        formatted_url = await asyncio.to_thread(os.getenv, "URL")
        formatted_url = formatted_url.format(since, until)
        pages = await how_many_pages_need_to_parse(formatted_url)
        tasks = [process_page(formatted_url, j) for j in range(1, pages + 1)]
        await asyncio.gather(*tasks)

async def main():
    await create_data_directory()
    await get_users_and_their_repositories()

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
