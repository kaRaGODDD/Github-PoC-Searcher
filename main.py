import asyncio

from dotenv import load_dotenv
from create_poc_database.create_poc_database import POCDatabase
from search_poc_through_github.poc_searcher import GithubPOCSearcher
from create_cve_database.create_cve_database import CVEDatabase


load_dotenv()

async def main():
    try:
        poc_instance = POCDatabase()
        cve_instance = CVEDatabase()
        await cve_instance.update_database(True)
        await poc_instance.update_database(True)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
