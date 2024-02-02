import asyncio
import aiohttp
import os
import re

from aiohttp import ServerDisconnectedError
from pydantic import ValidationError
from datetime import datetime
from dotenv import load_dotenv
from typing import List

from datetime_manager.create_datetime_intervals import create_intervals
from datetime_manager.return_last_date_and_current import return_last_current_intervals_for_poc_update

from file_manager.write_file_by_poc_pattern import write_poc_with_full_path, write_new_poc_object
from file_manager.process_of_distribution_poc import process_of_distribute_poc
from file_manager.distribution_of_objects import return_location_of_cve_object
from file_manager.read_files import read_file_by_path

from working_with_API.working_with_github_API import how_many_pages_by_query, return_data_from_query

from constants_and_other_stuff.returning_values import return_github_api_url
from constants_and_other_stuff.pydantic_models import HtmlUrlFromResponse, GraphQLAnswerModel
from constants_and_other_stuff.structs import CveModelForPoC, ProcessCVEID, StringInterval, NewPocObject, CveModelForPoC
from constants_and_other_stuff.enums import POCChoiceSearch, TypeOfTheDirectory, TypeOfPOCSearching
from constants_and_other_stuff.constants import GRAPHQL_QUERY

load_dotenv()

class PoCSearcher:
    '''Class represent PoC search in github'''
    def __init__(self,search_choice: POCChoiceSearch = POCChoiceSearch.GRAPHQL_SEARCH):
        self._github_token = os.getenv("GITHUB_TOKEN")
        self._name_of_the_poc_directory = os.getenv("NAME_OF_THE_POC_DIRECTORY")
        self._path_to_the_cve_database = os.getenv("PATH_TO_THE_DATA_DIRECTORY")
        self._url = os.getenv("GITHUB_API_URL")
        self._headers = {"Authorization": f"Bearer {self._github_token}"}
        self._search_choice = search_choice
        self._graphql_url = os.getenv("GITHUB_GRAPHQL_URL")
        self._special_url_for_update = os.getenv("GITHUB_SPECIAL_URL_FOR_UPDATE")

    async def start_search(self, type_of_poc_searching: TypeOfPOCSearching):
        while True:
            try:
                match type_of_poc_searching:
                    case TypeOfPOCSearching.TRAVERSE_ALL_CVE_DIRECTORY:
                        await self._traverse_cve_database_consistently()
                    case type_of_poc_searching.TRAVERSE_FIX_YEAR_ON_CVE_DIRECTORY:
                        print("Please input year ")
                        year = input()
                        if year > datetime.now().year:
                            raise Exception(f"That year {year} greater than current year")
                        await self._traverse_cve_database_by_year(year)
            except Exception as e:
                print(f"ServerDisconnectedError: {e}")
                print("Reconnecting...")
                await asyncio.sleep(5)
                continue
            else:
                break 

    async def update(self,rewrite_last_date_scrapping: bool=False):
        new_string_interval = await return_last_current_intervals_for_poc_update()
        query_intervals = await create_intervals(new_string_interval)
        await self._special_search_for_update(query_intervals)

    async def _traverse_cve_database(self):
        tasks = [self._traverse_cve_database_by_id(year) for year in range(1999,datetime.now().year+1)]
        await asyncio.gather(*tasks)

    async def _traverse_cve_database_consistently(self):
        for root, dirs, files in os.walk(self._path_to_the_cve_database):
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
                        print(cve_id)
                        poc_object = await self._generate_poc_object(cve_file_path, cve_need_to_processing)
                        await process_of_distribute_poc(cve_id, poc_object,self._search_choice)

    async def _traverse_cve_database_by_year(self, year: str):
        for root, dirs, files in os.walk(os.getenv("PATH_TO_THE_ASYNC_SCRAPPING").format(year)):
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
                        print(cve_id)
                        poc_object = await self._generate_poc_object(cve_file_path, cve_need_to_processing)
                        await process_of_distribute_poc(cve_id, poc_object,self._search_choice)


    async def _handle_cve_id(self,cve_id: str) -> ProcessCVEID:
        try:
            match self._search_choice:
                case POCChoiceSearch.GITHUB_API_SEARCH:
                    data = await self._create_request_on_cve_id(cve_id)
                    html_url_from_response = HtmlUrlFromResponse(**data)
                    return ProcessCVEID(html_url_from_response.total_count > 0,html_url_from_response.items)
                case POCChoiceSearch.GRAPHQL_SEARCH:
                    data = await self._create_post_request_on_cve_id_grapql_method(cve_id)
                    html_url_from_response = GraphQLAnswerModel(**data)
                    return ProcessCVEID(html_url_from_response.data.search.repositoryCount > 0, html_url_from_response.data.search.edges)
        except ValidationError as e:
                raise ValidationError(f"Validation error was occured {e}")

    async def _create_post_request_on_cve_id_grapql_method(self, cve_id: str) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                query = GRAPHQL_QUERY.format(cve_id)
                headers = {"Authorization": f"Bearer {self._github_token}"}

                async with session.post(url=self._graphql_url, json={"query": query}, headers=headers) as response:
                    response.raise_for_status()
                        
                    limit = int(response.headers.get("X-RateLimit-Remaining", 0))
                    reset_at_str = response.headers.get("X-RateLimit-Reset", "")
                    print(limit)
                    if not reset_at_str or limit <= 1:
                        reset_at = datetime.utcnow()
                        reset_at_unix_timestamp = int(reset_at_str)
                        reset_at = datetime.utcfromtimestamp(reset_at_unix_timestamp)
                        time_to_wait = max(0, (reset_at - datetime.utcnow()).total_seconds())
                            
                        if time_to_wait > 0:
                            print(f"Rate limit exceeded, waiting for {time_to_wait} seconds.")
                            await asyncio.sleep(time_to_wait + 4)
                    else:
                        await asyncio.sleep(0.33)

                    data = await response.json()
                    return data
        
        except ServerDisconnectedError as e:
            print(f"ServerDisconnectedError: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

                    
    async def _generate_poc_object(self,path_to_cve_file: str,cve_nned_to_processing: ProcessCVEID):
        content_from_file = await read_file_by_path(path_to_cve_file)
        description = await self._extract_description(content_from_file)
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
    
    async def _special_search_for_update(self,intervals: List[StringInterval]):
        for i in range(0,len(intervals)):
            since, until = intervals[i].first_interval, intervals[i].second_interval
            new_url = self._special_url_for_update.format(since,until)
            pages_on_query = await how_many_pages_by_query(new_url,per_search=30)
            tasks = [self._process_each_page(new_url,page) for page in range(0, pages_on_query + 1)]
            await asyncio.gather(*tasks)

    async def _process_each_page(self, new_url: str, page: int):
        data = await return_data_from_query(url=new_url,headers=self._headers,page=page)
        for item in data.get("items"):
            cve_id = await self._extract_cve_id(item.get("name"))
            if cve_id:
                pattern_of_cve_object_in_file = None
                pattern_of_poc_object_in_file = None
                path_to_poc_cve_object = await return_location_of_cve_object(cve_id, type_of_the_directory=TypeOfTheDirectory.PROOF_OF_CONCEPT_DIRECTORY)
                if os.path.exists(path_to_poc_cve_object):
                    pattern_of_poc_object_in_file = await read_file_by_path(path_to_poc_cve_object)
                    if pattern_of_poc_object_in_file is not None:
                        await self._working_with_extract_data(cve_id, pattern_of_poc_object_in_file, item.get("html_url"), path_to_poc_cve_object,
                                                            type_of_the_directory=TypeOfTheDirectory.PROOF_OF_CONCEPT_DIRECTORY)
                    else:
                        print(f"That cve {cve_id} was not added in processing query because returning value from reading the file is None")
                else:
                    path_to_cve_object = await return_location_of_cve_object(cve_id, type_of_the_directory=TypeOfTheDirectory.CVE_DATABASE_DIRECTORY)
                    pattern_of_cve_object_in_file = await read_file_by_path(path_to_cve_object)
                    if pattern_of_cve_object_in_file is not None:
                        await self._working_with_extract_data(cve_id, pattern_of_cve_object_in_file,item.get("html_url"), path_to_poc_cve_object,
                                                            type_of_the_directory=TypeOfTheDirectory.CVE_DATABASE_DIRECTORY)
                    print(f"That cve {cve_id} was not added in processing query because returning value from reading the file is None")
        
    async def _working_with_extract_data(self, cve_id: str, pattern_of_some_objects: str, new_github_url: str, 
                                     path_to_new_poc_object: str, type_of_the_directory: TypeOfTheDirectory):
        print(f"Working in extract data {cve_id}", type_of_the_directory.name)
        
        description = await self._extract_description(pattern_of_some_objects)
        
        if not description:
            path_to_cve_object = await return_location_of_cve_object(cve_id, type_of_the_directory=TypeOfTheDirectory.CVE_DATABASE_DIRECTORY)
            pattern_of_cve_object_in_file = await read_file_by_path(path_to_cve_object,TypeOfTheDirectory.CVE_DATABASE_DIRECTORY)
            if pattern_of_cve_object_in_file is None:
                print(f"No data in the file or the file doesn't exist for CVE: {cve_id}")
                return

            description = await self._extract_description(pattern_of_cve_object_in_file)

        match type_of_the_directory:
            case TypeOfTheDirectory.PROOF_OF_CONCEPT_DIRECTORY:
                all_references = await self._extract_all_references(pattern_of_some_objects)
                if new_github_url not in all_references:
                    all_references.append(new_github_url)
                cve_model = CveModelForPoC(description, all_references)
                await write_poc_with_full_path(cve_id, cve_model, path_to_new_poc_object, POCChoiceSearch.GITHUB_API_SEARCH)
            case TypeOfTheDirectory.CVE_DATABASE_DIRECTORY:
                new_poc_object = NewPocObject(description[0], new_github_url) 
                await write_new_poc_object(cve_id, new_poc_object, path_to_new_poc_object)


    async def _extract_all_references(self, cve_object: str) -> List[str]:
        return re.findall(r'(https://[0-9*?:;№"@!?><a-zA-z./-]+)', cve_object)

    async def _extract_description(self,content_from_file: str) -> str:
        return re.findall("`(.+?)`", content_from_file)

    async def _extract_cve_id(self, name_of_the_repository: str):
        matches = re.findall(r"([cC][vV][eE])-([0-9]{4})-([0-9]+)", name_of_the_repository)
        if matches:
            new_name_of_the_repository = "-".join(matches[0]).upper()
            return new_name_of_the_repository
        return ""


async def main():
    a = PoCSearcher()
    await a.start_search()

asyncio.run(main())
