import asyncio
import aiohttp
import aiofiles
import os
import re

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from github import Github

load_dotenv()
g = Github(os.getenv("TOKEN"))

async def get_urls_of_every_repos_on_page(url : str,query : str,pages : int):
    async with aiohttp.ClientSession() as session:
        for i in range(pages):
            async with session.get(url,params={"q": query,"page" : i}) as response:
                data = await response.json()
                for repo in data['items']:
                    print(repo['name'])
                    print(repo['description'])
                    print(repo['html_url'])
                    print("-" * 50)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(get_urls_of_every_repos_on_page("https://api.github.com/search/repositories","Proof of concept",10))


if __name__ == "__main__":
    asyncio.run(main())
