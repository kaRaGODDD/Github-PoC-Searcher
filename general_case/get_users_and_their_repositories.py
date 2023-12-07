import asyncio
import aiohttp
import aiofiles
import time

from dotenv import load_dotenv
from github import Github

load_dotenv()

async def get_urls_of_every_repos_on_page(url : str,query : str,pages : int):
    async with aiohttp.ClientSession() as session:
        for i in range(pages):
            async with session.get(url,params={"q": query,"page" : i}) as response:
                print(response.status)
                data = await response.json()
                for repo in data["items"]:
                    print(i,repo["owner"]["login"],repo["name"])
                time.sleep(10)


async def main():
    PAGES_COUNT = 100
    async with asyncio.TaskGroup() as tg:
        tg.create_task(get_urls_of_every_repos_on_page("https://api.github.com/search/repositories","Proof of concept",PAGES_COUNT))
        #https://api.github.com/search/repositories?q=Proof+of+concept&page=1

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
