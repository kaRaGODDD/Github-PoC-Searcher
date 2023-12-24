import asyncio
import aiohttp
import os
import time
import datetime

from dotenv import load_dotenv
from formed_datetime_intervals import generate_intervals
from math import ceil

load_dotenv()

async def how_many_pages_need_to_parse(url: str):
    PER_SEARCH = 30
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            count = data["total_count"]
    return ceil(count / PER_SEARCH)

async def clone_repository(repository_url: str):
    print(repository_url)
    try:
        process = await asyncio.create_subprocess_exec("git", "clone", repository_url + '.git')
        await process.wait()
    except Exception as e:
        print(f"Error cloning repository {repository_url}: {e}")

async def process_page(url: str, page: int):
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url + f"&page={page}",headers=headers) as response:
            data = await response.json()
            print(url + f"&page={page}")
            for item in data["items"]:
                os.chdir(os.getenv("PATH_TO_THE_DATA_DIRECTORY"))
                print(item["html_url"])
                await clone_repository(item["html_url"])

async def get_users_and_their_repositories():
    intervals = await generate_intervals(2015, 2016)
    for interval in intervals:
        since, until = interval
        formatted_url = await asyncio.to_thread(os.getenv, "URL")
        formatted_url = formatted_url.format(since, until)
        pages = await how_many_pages_need_to_parse(formatted_url)
        tasks = [process_page(formatted_url, i) for i in range(1, pages + 1)]
        await asyncio.gather(*tasks)

async def main():
    await get_users_and_their_repositories()

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)

