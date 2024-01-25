import asyncio
import aiohttp
import datetime
import os

from dotenv import load_dotenv
from pydantic import ValidationError
from typing import List

from file_manager.distribution_of_objects import process_and_distribute_cve
from file_manager.write_last_scrapping_date import write_last_date_scrapping
from datetime_manager.create_datetime_intervals import create_intervals
from constants_and_other_stuff.returning_values import return_nvd_api_url, return_nvd_api_key
from constants_and_other_stuff.pydantic_models import CveExploit
from constants_and_other_stuff.structs import StringInterval

load_dotenv()


class NvdDataBaseScrapper:
    def __init__(self, string_interval: StringInterval = StringInterval("2013-01-01", "2014-01-01")):
        self.string_interval = string_interval

    async def start_scrapping(self, rewrite_last_date_scrapping: bool=False):
        try:
            if rewrite_last_date_scrapping:
                await write_last_date_scrapping()
            await self._handle_intervals()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def update(self,rewrite_last_date_scrapping: bool=False):
        try:
            last_date_scrapping = os.getenv("LAST_DATE_SCRAPPING")
            current_date_scrapping = datetime.datetime.now().strftime("%Y-%m-%d")
            if last_date_scrapping is None:
                last_date_scrapping = datetime.datetime.now().strftime("%Y-%m-%d")
            await self.set_interval(StringInterval(last_date_scrapping,current_date_scrapping))
            await self.start_scrapping(rewrite_last_date_scrapping)
        except Exception as e:
            print(f"An unexpected error occurred method update: {e}")

    async def set_interval(self, new_string_interval: StringInterval):
        self.string_interval = new_string_interval

    async def _handle_api_request(self, url: str, string_interval: StringInterval, headers: dict[str, str]):
        try:
            data = await self._return_data_from_request(url, string_interval, headers)
            await self._handle_data(data.get("vulnerabilities", {}))
        except Exception as e:
            print(f"An unexpected error occurred method handle_api request: {e}", url)

    async def _handle_intervals(self):
        try:
            url = await return_nvd_api_url()
            nvd_api_key = await return_nvd_api_key()
            headers = {'apiKey': nvd_api_key}
            intervals = await create_intervals(self.string_interval)
            tasks = [self._handle_api_request(url.format(interval.first_interval, interval.second_interval), interval, headers) for interval in intervals]
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"An unexpected error occurred handle intervals: {e}")

    async def _handle_data(self, data: List[dict]):
        for cve_info in data:
            try:
                cve_exploit = CveExploit(**cve_info.get('cve', {}))
            except ValidationError as e:
                print("Exception", e.json())
            await process_and_distribute_cve(cve_exploit)

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
