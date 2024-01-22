import asyncio
import aiohttp
import os

from typing import List
from dotenv import load_dotenv
from pydantic import ValidationError
from file_manager.distribution_of_objects import distribute_cve_object
from datetime_manager.create_datetime_intervals import create_intervals
from constants_and_other_stuff.returning_values import return_nvd_api_url, return_nvd_api_key
from constants_and_other_stuff.pydantic_models import CveExploit
from constants_and_other_stuff.structs import StringInterval

load_dotenv()

#TODO add logger or loguru dont remember how to name that library
class NvdDataBaseScrapper:
    def __init__(self, string_interval: StringInterval):
        self.string_interval = string_interval

    async def start_scrapping(self):
        await self._handle_intervals()

    async def _handle_api_request(self,url: str, string_interval: StringInterval,headers: dict[str,str]):
        data = await self._return_data_from_request(url,string_interval,headers)
        await self._handle_data(data["vulnerabilities"])

    async def _handle_intervals(self):
        url = await return_nvd_api_url()
        nvd_api_key = await return_nvd_api_key()
        headers = { 'apiKey': nvd_api_key} 
        intervals = await create_intervals(self.string_interval)
        tasks = [self._handle_api_request(url,interval,headers) for interval in intervals]
        await asyncio.gather(*tasks)

    async def _handle_data(self,data: List[dict]):
        for cve_info in data:
            try:
                cve_exploit = CveExploit(**cve_info['cve'])
            except ValidationError as e:
                print("Exception",e.json())
            await distribute_cve_object(cve_exploit)

    async def _return_data_from_request(self, url: str, string_interval: StringInterval, headers: dict[str, str]):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url.format(string_interval.first_interval, string_interval.second_interval), headers=headers) as response:
                    if response.status != 200:
                        response.raise_for_status()
                    data = await response.json()
            return data
        except aiohttp.ClientResponseError as e:
            print(f"Error fetching data: {e}", url)
        except aiohttp.ClientError as e:
            print(f"Client error: {e}", url)
        except aiohttp.ContentTypeError as e:
            print(f"Content type error: {e}", url)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", url)

