import asyncio
import aiohttp
import os

from dotenv import load_dotenv
from datetime_manager.create_datetime_intervals import create_intervals
from constants_and_other_stuff.returning_values import return_nvd_api_url
from constants_and_other_stuff.structs import StringInterval

load_dotenv()

class NvdDataBaseScrapper:
    def __init__(self, string_interval: StringInterval):
        self.string_interval = string_interval

    async def start_scrapping(self):
        ''''''
        pass

    async def _handle_api_request(self,url: str, string_interval: StringInterval):
        data = await self._return_data_from_request(url,string_interval)
        '''TODO использовать pydantic для валидации! Перебор всех cve из data'''

    async def _return_data_from_request(self, url: str, string_interval: StringInterval):
        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(string_interval.first_interval, string_interval.second_interval)) as response:
                data = await response.json()
        return data

    async def _handle_intervals(self):
        url = await return_nvd_api_url()
        intervals = await create_intervals(self.string_interval)
        tasks = [self._handle_api_request(url,interval) for interval in intervals]
        asyncio.gather(*tasks)

async def main():
    ss = StringInterval("2015-03-01", "2015-03-06")
    asdf = NvdDataBaseScrapper(ss)
    await asdf._handle_intervals()
asyncio.run(main())