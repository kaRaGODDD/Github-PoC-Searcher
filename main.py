import asyncio

from dotenv import load_dotenv
from create_poc_database.create_poc_database import POCDatabase
from create_cve_database.create_cve_database import CVEDatabase
from poc_download.github_poc_download import GithubPOCDownloader

load_dotenv()

async def main():
    try:
        poc_instance = POCDatabase()
        cve_instance = CVEDatabase()
        poc_downloader_instance = GithubPOCDownloader()
        #await cve_instance.update_database(True)
        #await poc_instance.update_database(True)
        await poc_downloader_instance.start_download()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
  