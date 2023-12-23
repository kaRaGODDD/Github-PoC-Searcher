import asyncio
import aiohttp
import aiofiles
import time
import os
import json

from pydantic import BaseModel
from dotenv import load_dotenv
from github import Github
from processing_repositories import processing_repository
from math import ceil
from datetime import datetime
from typing import Optional

from create_directories import create_directory_by_user_name

load_dotenv()

async def how_many_pages_need_to_parse(url : str):
    PER_SEARCH = 30
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            count = data["total_count"]
    return ceil(count / PER_SEARCH)

async def get_users_and_their_repositories():
    #since and until just some constants 
    since = datetime(2015,2,16)
    until = datetime(2015,3,12)
    url = await asyncio.to_thread(os.getenv,"URL")
    url = url.format(since.strftime("%Y-%m-%d"),until.strftime("%Y-%m-%d"))
    pages = await how_many_pages_need_to_parse(url)
    for i in range(1,pages + 1):
        async with aiohttp.ClientSession() as session:
            async with session.get(url + f"&page={i}") as response:
                data = await response.json()
                print(url + f"&page={i}")
                for item in data["items"]:
                    await create_directory_by_user_name(item["owner"]["login"])
                    await processing_repository(item["owner"]["login"],item["name"])

async def main():
    await get_users_and_their_repositories()
     #TODO make array list with time data need which i need to parse
     #https://api.github.com/search/repositories?q=Proof+of+concept&page=1

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
