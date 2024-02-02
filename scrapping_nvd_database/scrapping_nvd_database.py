import asyncio
import aiohttp
import datetime
import os

from dotenv import load_dotenv
from pydantic import ValidationError
from typing import List, Optional

from file_manager.distribution_of_objects import process_and_distribute_cve
from file_manager.write_last_scrapping_date import write_last_date_scrapping
from datetime_manager.create_datetime_intervals import create_intervals
from constants_and_other_stuff.returning_values import return_nvd_api_url, return_nvd_api_key
from constants_and_other_stuff.pydantic_models import CveExploit
from constants_and_other_stuff.structs import StringInterval
from constants_and_other_stuff.enums import FileSaving, TypeOfScrapping

load_dotenv()


class NvdDataBaseScrapper:
    def __init__(self, string_interval: StringInterval = StringInterval("2013-01-01", "2014-01-01"), 
                 file_saving: FileSaving = FileSaving.MD):
        self.string_interval = string_interval
        self._file_saving = file_saving
        self._url = os.getenv("NVD_API_URL")
        self._nvd_api_key = os.getenv("NVD_API_KEY")
        self._headers = {'apiKey':self._nvd_api_key}

    async def start_scrapping(self, rewrite_last_date_scrapping: bool=False, type_of_scrapping: TypeOfScrapping=TypeOfScrapping.SCRAPPING):
        try:
            if rewrite_last_date_scrapping:
                await write_last_date_scrapping("LAST_SCRAPPING_DATE_OF_NVD")
            await self._handle_intervals(type_of_scrapping)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def update(self,rewrite_last_date_scrapping: bool=False, last_date_scrapping: str="2024-01-01T00:00:00"):
        try:
            current_date_scrapping = datetime.datetime.now().strftime("%Y-%m-%d")
            if last_date_scrapping is None:
                last_date_scrapping = datetime.datetime.now().strftime("%Y-%m-%d")
            await self.set_interval(StringInterval(last_date_scrapping, current_date_scrapping))
            await self.start_scrapping(rewrite_last_date_scrapping, type_of_scrapping=TypeOfScrapping.UPDATE)
        except Exception as e:
            print(f"An unexpected error occurred method update: {e}")

    async def set_interval(self, new_string_interval: StringInterval):
        self.string_interval = new_string_interval
    
    async def set_file_saving_status(self,file_saving: FileSaving):
        self._file_saving = file_saving

    async def _handle_api_request(self, url: str, string_interval: StringInterval, headers: dict[str, str]):
        try:
            data = await self._return_data_from_request(url, string_interval, headers)
            match self._file_saving:
                case FileSaving.MD:
                    await self._handle_data(data.get("vulnerabilities", {}))
                case FileSaving.JSON:
                    await self._handle_data(data.get("vulnerabilities", {}),data)
        except Exception as e:
            print(f"An unexpected error occurred method handle_api request: {e}", url)

    async def _handle_intervals(self, type_of_scrapping: TypeOfScrapping = TypeOfScrapping.SCRAPPING):
        try:
            intervals = await create_intervals(self.string_interval)
            match type_of_scrapping:
                case TypeOfScrapping.SCRAPPING:
                    tasks = [self._handle_api_request(self._url.format(interval.first_interval + "T" + "00:00:00", interval.second_interval + "T" + "23:59:59"),
                                              interval, self._headers) for interval in intervals]
                case TypeOfScrapping.UPDATE:
                    tasks = [self._handle_api_request(self._url.format(interval.first_interval + "T" + "00:00:00" , interval.second_interval + "T" + datetime.datetime.now().strftime("%H:%M:%S")),
                                              interval, self._headers) for interval in intervals]
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"An unexpected error occurred handle intervals: {e}")

    async def _handle_data(self, data: List[dict], json_answer: Optional[dict]={}):
        for cve_info in data:
            try:
                cve_exploit = CveExploit(**cve_info.get('cve', {}))
            except ValidationError as e:
                print("Exception", e.json())
            match self._file_saving:
                case FileSaving.MD:
                    await process_and_distribute_cve(cve_exploit,self._file_saving)
                case FileSaving.JSON:
                    await process_and_distribute_cve(cve_exploit,self._file_saving,json_answer=cve_info)

    async def _return_data_from_request(self, url: str, string_interval: StringInterval, headers: dict[str, str]) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
            return data
        except aiohttp.ClientResponseError as e:
            print(f"Error fetching data: {e}", url)
        except aiohttp.ClientError as e:
            print(f"Client error: {e}", url)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", url)
