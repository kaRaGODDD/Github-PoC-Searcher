import asyncio
import aiohttp
import os
import re

from pydantic import ValidationError
from dotenv import load_dotenv
from constants_and_other_stuff.returning_values import return_github_api_url
from file_manager.process_of_distribution_poc import process_of_distribute_poc
from file_manager.read_files import read_file_by_path
from constants_and_other_stuff.pydantic_models import HtmlUrlFromResponse
from constants_and_other_stuff.structs import CveModelForPoC, ProcessCVEID

load_dotenv()

class PoCSearcher:
    def __init__(self):
        self._github_token = os.getenv("GITHUB_TOKEN")
        self._name_of_the_poc_directory = os.getenv("NAME_OF_THE_POC_DIRECTORY")
        self._path_to_the_cve_database = os.getenv("PATH_TO_THE_DATA_DIRECTORY")
        self._url = os.getenv("GITHUB_API_URL")
        self._headers = {"Authorization": f"Bearer {self._github_token}"}


    async def start_search(self):
        await self._traverse_cve_database()

    async def update(self,rewrite_last_date_scrapping: bool=False):
        ...

    async def _traverse_cve_database(self):
        for root, dirs, files in os.walk(self._path_to_the_cve_database):
            if '.git' in dirs:
                dirs.remove('.git')
            for file in files:
                if file != "README.md":
                    cve_file_path = os.path.join(root, file)
                    cve_id = os.path.splitext(file)[0]
                    print(cve_id)
                    cve_need_to_processing = await self._handle_cve_id(cve_id)
                    if cve_need_to_processing.need:
                        poc_object = await self._generate_poc_object(cve_file_path, cve_need_to_processing)
                        #Тут вот добавить task group
                        await process_of_distribute_poc(cve_id, poc_object)

    async def _handle_cve_id(self,cve_id: str) -> ProcessCVEID:
        try:
            data = await self._create_request_on_cve_id(cve_id)
            html_url_from_response = HtmlUrlFromResponse(**data)
        except ValidationError as e:
                raise ValidationError(f"Validation error was occured {e}")
        return ProcessCVEID(html_url_from_response.total_count > 0,html_url_from_response.items)

    async def _generate_poc_object(self,path_to_cve_file: str,cve_nned_to_processing: ProcessCVEID ):
        content_from_file = await read_file_by_path(path_to_cve_file)
        description = await self._collect_description(content_from_file)
        return CveModelForPoC(description,cve_nned_to_processing.github_urls)
    
    async def _create_request_on_cve_id(self, cve_id: str) -> dict:
        try:        
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url.format(cve_id), headers=self._headers) as response:
                    response.raise_for_status()
                    await asyncio.sleep(2)
                    data = await response.json()
                    remaining_requests = response.headers.get('X-RateLimit-Remaining')
                    total_requests = response.headers.get('X-RateLimit-Limit')
                    print(f"Requests remaining: {remaining_requests}")
                    print(f"Total requests allowed: {total_requests}")
                    return data
        except aiohttp.ClientResponseError as e:
            print(f"Error fetching data: {e}")
        except aiohttp.ClientError as e:
            print(f"Client error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def _collect_description(self,content_from_file: str) -> str:
        return re.findall("`(.+?)`",content_from_file)
    
    async def _parse_contents_of_the_cve_file(self):
        ...
    async def _clone_that_repositories(self):
        ...

async def main():
    a = PoCSearcher()
    await a.start_search()

asyncio.run(main())
