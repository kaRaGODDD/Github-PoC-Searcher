import asyncio
import aiohttp
import aiofiles
import time
import json

from pydantic import BaseModel
from dotenv import load_dotenv
from github import Github
from processing_repositories import processing_repository

load_dotenv()

class Repository(BaseModel):
    name : str
    owner : dict
    url : str

async def get_urls_of_every_repos_on_page(url : str,query : str,pages : int):
    async with aiohttp.ClientSession() as session:
        for i in range(pages):
            async with session.get(url,params={"q": query,"page" : i}) as response:
                data = await response.json()
                for repo in data["items"]:
                    repo_data = Repository(**repo)
                    #print(repo_data.name,repo_data.owner["login"])
                     await processing_repository(repo_data.name, repo_data.owner["login"])


async def main():
    PAGES_COUNT = 1
    async with asyncio.TaskGroup() as tg:
        tg.create_task(get_urls_of_every_repos_on_page("https://api.github.com/search/repositories","Proof of concept",PAGES_COUNT))
        #https://api.github.com/search/repositories?q=Proof+of+concept&page=1

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
