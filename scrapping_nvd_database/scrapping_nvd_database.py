import asyncio
import aiohttp
import datetime
import os

from math import ceil
from dotenv import load_dotenv
from pydantic import ValidationError
from typing import List, Optional, Union
from loguru import logger

from file_manager.distribution_of_objects import process_and_distribute_cve
from file_manager.write_last_scrapping_date import write_last_date_scraping

from datetime_manager.create_datetime_intervals import create_intervals

from constants_and_other_stuff.pydantic_models import CveExploit
from constants_and_other_stuff.structs import StringInterval
from constants_and_other_stuff.enums import FileFormat, ScrapingType, Sources


load_dotenv()

logger.add('logs/NVD.log', rotation="8:00", level="DEBUG", compression="zip")


class NVDScraper:
    def __init__(self, string_interval: StringInterval = StringInterval("2013-01-01", "2014-01-01"),
                  file_format: FileFormat = FileFormat.MD):
        required_env_variables = ["NVD_API_URL", "NVD_API_KEY"]
        missing_env_variables = [env_var for env_var in required_env_variables if os.getenv(env_var) is None]

        if missing_env_variables:
            logger.critical(f"Critical error: Missing required environment variables for NVDScraper: {', '.join(missing_env_variables)}")
            raise Exception(f"Critical error: Missing required environment variables for NVDScraper: {', '.join(missing_env_variables)}")
        
        self.string_interval = string_interval
        self._file_format = file_format
        self._url = os.getenv("NVD_API_URL")  
        self._nvd_api_key = os.getenv("NVD_API_KEY")
        self._headers = {'apiKey':self._nvd_api_key}

    async def start_scraping(self, rewrite_last_date_scraping: bool=False, type_of_scraping: ScrapingType=ScrapingType.SCRAPING):
        try:
            if rewrite_last_date_scraping:
                await write_last_date_scraping("LAST_SCRAPPING_DATE_OF_NVD")
            await self._handle_intervals(type_of_scraping)
        except Exception as e:
            logger.warning(f"An unexpected error occurred in function start scraping {e}")

    async def update(self,rewrite_last_date_scrapping: bool=False, last_date_scrapping: str="2024-01-01"):
        try:
            current_date_scrapping = datetime.datetime.now().strftime("%Y-%m-%d")
            if last_date_scrapping is None:
                last_date_scrapping = datetime.datetime.now().strftime("%Y-%m-%d")
            await self.set_interval(StringInterval(last_date_scrapping, current_date_scrapping))
            await self.start_scraping(rewrite_last_date_scrapping, type_of_scraping=ScrapingType.UPDATE)
        except Exception as e:
            logger.warning(f"An unexpected error occurred in function update {e}")

    async def set_interval(self, new_string_interval: StringInterval):
        self.string_interval = new_string_interval
    
    async def set_file_saving_status(self, file_saving: FileFormat):
        self._file_format = file_saving

    async def _handle_intervals(self, type_of_scrapping: ScrapingType = ScrapingType.SCRAPING):
        try:
            intervals = await create_intervals(self.string_interval, Sources.NVD)
            match type_of_scrapping:
                case ScrapingType.SCRAPING:
                    tasks = [self._handle_api_request(self._url.format(interval.first_interval + "T" + "00:00:00", interval.second_interval + "T" + "23:59:59"),
                                              interval) for interval in intervals]
                case ScrapingType.UPDATE:
                    tasks = [self._handle_api_request(self._url.format(interval.first_interval + "T" + "00:00:00" , interval.second_interval + "T" + datetime.datetime.now().strftime("%H:%M:%S")),
                                              interval) for interval in intervals]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.warning(f"An unexpected error occurred handle intervals: {e}")

    async def _handle_api_request(self, url: str, string_interval: StringInterval):
        try:
            how_many_pages_need_to_process = await self._return_total_result_per_query(url, string_interval)
            for page in range(0, how_many_pages_need_to_process):
                data = await self._return_data_from_request(url, string_interval, start_index=page*2000, per_page=2000)
                match self._file_format: 
                    case FileFormat.MD:
                        await self._handle_data(data.get("vulnerabilities", {}))
                    case FileFormat.JSON:
                        await self._handle_data(data.get("vulnerabilities", {}),data)
        except Exception as e:
            logger.warning(f"An unexpected error occurred method handle_api request: {e}", url)

    async def _handle_data(self, data: List[dict], json_answer: Optional[dict]={}):
        for cve_info in data:
            try:
                cve_exploit = CveExploit(**cve_info.get('cve', {}))
            except ValidationError as e:
                logger.error("Exception was occured while function handle data try to validate data", e.json())
            match self._file_format:
                case FileFormat.MD:
                    await process_and_distribute_cve(cve_exploit,self._file_format)
                case FileFormat.JSON:
                    await process_and_distribute_cve(cve_exploit,self._file_format,json_answer=cve_info)

    async def _return_total_result_per_query(self, url: str, string_interval: StringInterval) -> int:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._headers) as response:
                   response.raise_for_status()
                   data = await response.json()
            return ceil(data.get('totalResults', 0) / 2000)
        except Exception as e:
            logger.warning(f"Some exception was occured in return result per query", {e})

    async def _return_data_from_request(self, url: str, string_interval: StringInterval, start_index: int, per_page: int) -> Union[dict, None]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url + f"&startIndex={start_index}&resultsPerPage={per_page}",headers=self._headers) as response:
                    response.raise_for_status()
                    data = await response.json()
            return data
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error fetching data: {e}", url)
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {e}", url)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", url)

async def main():
    a = NVDScraper(StringInterval("2021-08-04","2021-10-22"))
    await a.start_scraping()

asyncio.run(main())