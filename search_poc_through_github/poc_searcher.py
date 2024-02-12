import asyncio
import aiohttp
import os
import re

from aiohttp import ServerDisconnectedError
from datetime import datetime
from dotenv import load_dotenv
from pydantic import ValidationError
from loguru import logger
from typing import List

from datetime_manager.create_datetime_intervals import create_intervals
from datetime_manager.return_last_date_and_current import return_last_current_intervals_for_poc_update

from file_manager.write_file_by_poc_pattern import write_poc_with_full_path, write_new_poc_object
from file_manager.process_of_distribution_poc import process_of_distribute_poc
from file_manager.distribution_of_objects import return_location_of_cve_object
from file_manager.read_files import read_file_by_path

from working_with_API.working_with_github_API import how_many_pages_by_query, return_data_from_query

from constants_and_other_stuff.returning_values import return_github_api_url
from constants_and_other_stuff.pydantic_models import UrlFromResponse, GraphQLAnswerModel, FastSearchValidator, RepositoryContent, TopicContent
from constants_and_other_stuff.structs import POCModel, CVEIDProcessing, StringInterval, POCObject, POCModel
from constants_and_other_stuff.enums import POCSearchMethod, DirectoryType, POCSearchType, CveIDFromDifferentSources
from constants_and_other_stuff.constants import GRAPHQL_QUERY, GRAPHQL_QUERY_FOR_FAST_INTERVAL_SEACH


load_dotenv()

logger.add('logs/github_searcher.log', rotation="8:00", level="DEBUG", compression="zip")


class GithubPOCSearcher:
    '''Class represent PoC search in github'''
    def __init__(self,search_choice: POCSearchMethod = POCSearchMethod.GRAPHQL_SEARCH):
        self._github_token = os.getenv("GITHUB_TOKEN")
        self._name_of_the_poc_directory = os.getenv("NAME_OF_THE_POC_DIRECTORY")
        self._path_to_the_cve_database = os.getenv("PATH_TO_THE_DATA_DIRECTORY")
        self._url = os.getenv("GITHUB_API_URL")   
        self._headers = {"Authorization": f"Bearer {self._github_token}"}
        self._search_choice = search_choice
        self._graphql_url = os.getenv("GITHUB_GRAPHQL_URL")
        self._special_url_for_update = os.getenv("GITHUB_SPECIAL_URL_FOR_UPDATE")

    async def start_search_by_traverse_directory(self, type_of_poc_searching: POCSearchType):
        while True:
            try:
                match type_of_poc_searching:
                    case POCSearchType.TRAVERSE_ALL_CVE_DIRECTORIES_CONSISTENTLY:
                        await self._traverse_cve_database_on_pc_by_path(self._path_to_the_cve_database)
                    case POCSearchType.TRAVERSE_FIX_YEAR_ON_CVE_DIRECTORY:
                        year = await self._prepare_for_fix_year_scrapping()
                        await self._traverse_cve_database_on_pc_by_path(os.getenv("PATH_TO_CVE_YEAR_DIRECTORY").format(year))
                    case POCSearchType.TRAVERSE_ALL_DIRECTORIES_AT_ONCE:
                        await self._traverse_cve_database_all_directories_at_once()
            except Exception as e:
                logger.warning(f"ServerDisconnectedError: {e}")
                logger.warning("Reconnecting...")
                await asyncio.sleep(5)
                continue
            else:
                break 
    
    async def start_search(self, string_interval: StringInterval):
        '''Alternative search poc`s throught github with help of Graphql'''
        query_intervals = await create_intervals(string_interval)
        await self._generate_pages_for_request(query_intervals)

    async def _generate_pages_for_request(self, intervals: List[StringInterval]):
        '''Handle each interval from list'''
        tasks = [(self._process_each_page(intervals[i])) for i in range(0, len(intervals))]
        await asyncio.gather(*tasks)
 
    async def _process_each_page(self, string_date_interval: StringInterval):
        '''Puprose to handle data from request'''
        try:
            data = await self._get_data_for_fast_search(string_date_interval)
            distribution_data = FastSearchValidator(**data)
            await self._processing_data_from_fast_search_validator(distribution_data.data.search.edges)
        except ValidationError as e:
            logger.warning(f"Validation error of second version of process page {e}")
    
    async def _get_data_for_fast_search(self, string_date_interval: StringInterval):
        '''For second version of fast search to make a post request'''
        try:
            query = GRAPHQL_QUERY_FOR_FAST_INTERVAL_SEACH.format(string_date_interval.first_interval, string_date_interval.second_interval)
            async with aiohttp.ClientSession() as session:
                async with session.post(url=self._graphql_url, json={"query": query}, headers=self._headers) as response:
                    remaining_requests = response.headers.get('X-RateLimit-Remaining')
                    logger.debug(f"Remaining requests {remaining_requests}")
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except ServerDisconnectedError as e:
            logger.warning(f"ServerDisconnectedError: {e}")
            raise
        except Exception as e:
            logger.warning(f"An unexpected error occurred: {e}")
            raise
        
    async def _processing_data_from_fast_search_validator(self, data_need_to_distribute: List[RepositoryContent]):
        '''Purpose to distribute the cve'''
        for value in data_need_to_distribute:
            cve_ids_from_repository_name = await self._extract_cve_ids(value.node.name)
            cve_ids_from_repository_description = await self._extract_cve_ids(value.node.description)
            if cve_ids_from_repository_name:
                await self._process_each_cve_id_v2(cve_ids_from_repository_name, value.node.url)
            elif cve_ids_from_repository_description:
                await self._process_each_cve_id_v2(cve_ids_from_repository_description, value.node.url)
            else:
                combine_all_topics = await self._get_all_topics_in_one_string(value.node.repositoryTopics.edges)
                if combine_all_topics:
                    cve_ids_from_repository_topics = await self._extract_cve_ids(combine_all_topics)
                    if cve_ids_from_repository_topics:
                        await self._process_each_cve_id_v2(cve_ids_from_repository_topics, value.node.url)
        
    async def _process_each_cve_id_v2(self, lst_of_cve_ids: List[str], repository_html_url: str):
        '''Send each cve to handler'''
        for cve_id in lst_of_cve_ids:
            if await self._is_valid(cve_id):
                await self._process_each_cve_id_from_different_sources_v2(cve_id, repository_html_url)
        
    async def _is_valid(self, cve_id: str):
        '''Check the valid of cve id'''
        return 1999 <= int(cve_id.split("-")[1]) <= datetime.now().year

    async def _process_each_cve_id_from_different_sources_v2(self, cve_id: str, html_url: str):
        '''Prepairing data for each cve to '''
        pattern_of_cve_object_in_file = None
        pattern_of_poc_object_in_file = None
        path_to_poc_cve_object = await return_location_of_cve_object(cve_id, type_of_the_directory=DirectoryType.POC_DIRECTORY)
        if os.path.exists(path_to_poc_cve_object):
            pattern_of_poc_object_in_file = await read_file_by_path(path_to_poc_cve_object)
            if pattern_of_poc_object_in_file is not None:
                await self._working_with_extract_data(cve_id, pattern_of_poc_object_in_file, html_url,
                                                       path_to_poc_cve_object, type_of_the_directory=DirectoryType.POC_DIRECTORY)
            else:
                logger.error(f"That cve {cve_id} was not added in processing query because returning value from reading the file is None")
        else:
            path_to_cve_object = await return_location_of_cve_object(cve_id, type_of_the_directory=DirectoryType.CVE_DATABASE_DIRECTORY)
            pattern_of_cve_object_in_file = await read_file_by_path(path_to_cve_object)
            if pattern_of_cve_object_in_file is not None:
                await self._working_with_extract_data(cve_id, pattern_of_cve_object_in_file, html_url,
                                                       path_to_poc_cve_object, type_of_the_directory=DirectoryType.CVE_DATABASE_DIRECTORY)
            else:
                logger.error(f"That cve {cve_id} was not added in processing query because returning value from reading the file is None")

    async def _get_all_topics_in_one_string(self, list_of_topics: List[TopicContent]) -> str:
        topic_list = [each_topic.node.topic.name for each_topic in list_of_topics]
        topic_string = " ".join(topic_list)
        return topic_string
        
    async def update(self, rewrite_last_date_scrapping: bool=False):
        new_string_interval = await return_last_current_intervals_for_poc_update()
        await self.start_search(new_string_interval)

    async def _traverse_cve_database_all_directories_at_once(self):
        tasks = [
            self._traverse_cve_database_on_pc_by_path(os.getenv("PATH_TO_CVE_YEAR_DIRECTORY").format(year))
            for year in range(1999, datetime.now().year + 1)
        ]
        await asyncio.gather(*tasks)

    async def _traverse_cve_database_on_pc_by_path(self, path: str):
        for root, dirs, files in os.walk(path):
            if '.git' in dirs:
                dirs.remove('.git')
            if os.getenv("NAME_OF_THE_JSON_AWSWERS_DIRECTORY") in dirs:
                dirs.remove(os.getenv("NAME_OF_THE_JSON_AWSWERS_DIRECTORY"))
            for file in files:
                if file != "README.md":
                    cve_file_path = os.path.join(root, file)
                    cve_id = os.path.splitext(file)[0]
                    cve_need_to_processing = await self._handle_cve_id(cve_id)
                    if cve_need_to_processing.need:
                        logger.debug(cve_id)
                        poc_object = await self._generate_poc_object(cve_file_path, cve_need_to_processing)
                        await process_of_distribute_poc(cve_id, poc_object,self._search_choice)

    async def _prepare_for_fix_year_scrapping(self) -> str:
        print("Please input year ")
        year = input()
        if int(year) > datetime.now().year:
            raise Exception(f"That year {year} greater than current year")
        return year

    async def _handle_cve_id(self, cve_id: str) -> CVEIDProcessing:
        try:
            match self._search_choice:
                case POCSearchMethod.GITHUB_API_SEARCH:
                    data = await self._create_request_on_cve_id(cve_id)
                    items_from_api_answer = UrlFromResponse(**data)
                    return CVEIDProcessing(items_from_api_answer.total_count > 0,items_from_api_answer.items)
                case POCSearchMethod.GRAPHQL_SEARCH:
                    data = await self._create_post_request_on_cve_id_grapql_method(cve_id)
                    items_from_api_answer = GraphQLAnswerModel(**data)
                    return CVEIDProcessing(items_from_api_answer.data.search.repositoryCount > 0, items_from_api_answer.data.search.edges)
        except ValidationError as e:
                logger.warning(f"Validation error was occured in function handle cve id {e}")
                raise ValidationError
        
    async def _wait_before_next_request(self, response: aiohttp.ClientResponse):
        limit = int(response.headers.get("X-RateLimit-Remaining", 0))
        reset_at_str = response.headers.get("X-RateLimit-Reset", "")
        DELTA = 3
        logger.debug(f"Wait before next request function remaining {limit}")
        if not reset_at_str or limit <= datetime.now().year % 100:
            reset_at = datetime.utcnow()
            reset_at_unix_timestamp = int(reset_at_str)
            reset_at = datetime.utcfromtimestamp(reset_at_unix_timestamp)
            time_to_wait = max(0, (reset_at - datetime.utcnow()).total_seconds())                
            if time_to_wait > 0:
                logger.debug(f"Rate limit exceeded, waiting for {time_to_wait} seconds.")
                await asyncio.sleep(time_to_wait + DELTA)
        else:
            await asyncio.sleep(0.33)

    async def _create_post_request_on_cve_id_grapql_method(self, cve_id: str) -> dict:
        try:
            query = GRAPHQL_QUERY.format(cve_id)
            async with aiohttp.ClientSession() as session:
                async with session.post(url=self._graphql_url, json={"query": query}, headers=self._headers) as response:
                    response.raise_for_status()
                    await self._wait_before_next_request(response)
                    data = await response.json()
                    return data
        except ServerDisconnectedError as e:
            logger.warning(f"ServerDisconnectedError: {e}")
            raise
        except Exception as e:
            logger.warning(f"An unexpected error occurred: {e}")
            raise
                    
    async def _generate_poc_object(self,path_to_cve_file: str, cve_need_to_processing: CVEIDProcessing):
        content_from_file = await read_file_by_path(path_to_cve_file)
        description = await self._extract_description(content_from_file)
        return POCModel(description, cve_need_to_processing.github_urls)
    
    async def _create_request_on_cve_id(self, cve_id: str) -> dict:
        try:        
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url.format(cve_id), headers=self._headers) as response:
                    response.raise_for_status()
                    await asyncio.sleep(2)
                    data = await response.json()
                    remaining_requests = response.headers.get('X-RateLimit-Remaining')
                    total_requests = response.headers.get('X-RateLimit-Limit')
                    logger.debug(f"Requests remaining: {remaining_requests}")
                    logger.debug(f"Total requests allowed: {total_requests}")
                    return data
        except aiohttp.ClientResponseError as e:
            logger.warning(f"Error fetching data: {e}")
        except aiohttp.ClientError as e:
            logger.warning(f"Client error: {e}")
        except Exception as e:
            logger.warning(f"An unexpected error occurred: {e}")
        
    async def _working_with_extract_data(self, cve_id: str, pattern_of_some_objects: str, new_github_url: str, 
                                     path_to_new_poc_object: str, type_of_the_directory: DirectoryType):
        '''Get data for cve: description, urls, name'''
        description = await self._extract_description(pattern_of_some_objects)
        
        if not description:
            path_to_cve_object = await return_location_of_cve_object(cve_id, type_of_the_directory=DirectoryType.CVE_DATABASE_DIRECTORY)
            pattern_of_cve_object_in_file = await read_file_by_path(path_to_cve_object, DirectoryType.CVE_DATABASE_DIRECTORY)
            if pattern_of_cve_object_in_file is None:
                logger.warning(f"No data in the file or the file doesn't exist for CVE: {cve_id}")
                return

            description = await self._extract_description(pattern_of_cve_object_in_file)

        match type_of_the_directory:
            case DirectoryType.POC_DIRECTORY:
                all_references = await self._extract_all_references(pattern_of_some_objects)
                if new_github_url not in all_references:
                    all_references.append(new_github_url)
                    cve_model = POCModel(description, all_references)
                    await write_poc_with_full_path(cve_id, cve_model, path_to_new_poc_object, POCSearchMethod.GITHUB_API_SEARCH)
                else:
                    return
            case DirectoryType.CVE_DATABASE_DIRECTORY:
                if description:
                    new_poc_object = POCObject(description[0], new_github_url)
                else:
                    new_poc_object = POCObject("", new_github_url) 
                await write_new_poc_object(cve_id, new_poc_object, path_to_new_poc_object)

    async def _get_topics_from_api_answer(self, api_answer: dict) -> List[str]:
        return api_answer.get("topics")

    async def _extract_all_references(self, cve_object: str) -> List[str]:
        return re.findall(r'(https://[0-9*?:;№"@!?><a-zA-z./-]+)', cve_object)

    async def _extract_description(self,content_from_file: str) -> List[str]:
        return re.findall("`(.+?)`", content_from_file)
    
    async def _extract_cve_ids(self, field_with_possible_cve_id: str) -> List[str]:
        if field_with_possible_cve_id is not None:
            matches = re.findall(r"([cC][vV][eE])[-_ ]?([0-9]{4})[-_ ]?([0-9]+)", field_with_possible_cve_id)
            cve_ids = []
            for match in matches:
                cve_id = f"CVE-{match[1]}-{match[2]}"
                cve_ids.append(cve_id)
            return cve_ids
        return []

async def main():
    a = GithubPOCSearcher()
    await a.start_search(StringInterval("2024-01-01", "2024-02-12"))  

asyncio.run(main())