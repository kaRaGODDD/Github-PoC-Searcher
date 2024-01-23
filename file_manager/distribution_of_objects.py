import asyncio
import aiofiles
import os
import re

import math
from dotenv import load_dotenv
from constants_and_other_stuff.structs import ComponentsOfCveID
from constants_and_other_stuff.pydantic_models import CveExploit
from file_manager.write_file import write_file_by_pattern
from create_directories.create_directories_on_pc import create_directory

load_dotenv()

async def distribute_cve_object(cve_object: CveExploit):
    split_data = await _split_cve_into_components(cve_object.id)
    await _parse_cve_object_by_year(split_data)
    await _parse_cve_object_by_id(split_data)
    await write_file_by_pattern(cve_object)

async def _parse_cve_object_by_year(cve_object: ComponentsOfCveID):
    await create_directory(os.getenv("NAME_OF_THE_DATA_DIRECTORY"),os.getenv("PATH_TO_THE_BASE_DIRECTORY"))
    await create_directory(cve_object.cve_year,os.getenv("PATH_TO_THE_DATA_DIRECTORY"))        

async def _parse_cve_object_by_id(cve_object: ComponentsOfCveID):
    determine_folder_name_by_formula = await _determine_folder_name(cve_object)
    full_path = os.path.join(os.getenv("PATH_TO_THE_DATA_DIRECTORY"),cve_object.cve_year)
    await create_directory(determine_folder_name_by_formula,full_path)

async def _determine_folder_name(cve_obj: ComponentsOfCveID):
    s = str((int(cve_obj.cve_id) / 1000)).split(".")
    folder_name = s[0] + ''.join(['x' for _ in range(len(s[1]))])
    return folder_name

async def _split_cve_into_components(cve_id: str) -> ComponentsOfCveID:
    split_object = cve_id.split('-')
    return ComponentsOfCveID(split_object[0],split_object[1],split_object[2])
