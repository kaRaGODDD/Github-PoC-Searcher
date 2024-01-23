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

async def process_and_distribute_cve(cve_object: CveExploit):
    split_data = await _extract_cve_components(cve_object.id)
    await _create_yearly_directories(split_data)
    path = await _create_id_based_directory(split_data)
    await write_file_by_pattern(cve_object, path)

async def _create_yearly_directories(cve_object: ComponentsOfCveID):
    await create_directory(os.getenv("NAME_OF_THE_DATA_DIRECTORY"), os.getenv("PATH_TO_THE_BASE_DIRECTORY"))
    await create_directory(cve_object.cve_year, os.getenv("PATH_TO_THE_DATA_DIRECTORY"))

async def _create_id_based_directory(cve_object: ComponentsOfCveID) -> str:
    determine_folder_name_by_formula = await _generate_folder_name(cve_object)
    full_path = os.path.join(os.getenv("PATH_TO_THE_DATA_DIRECTORY"), cve_object.cve_year)
    await create_directory(determine_folder_name_by_formula, full_path)
    return full_path

async def _generate_folder_name(cve_obj: ComponentsOfCveID):
    s = str((int(cve_obj.cve_id) / 1000)).split(".")
    folder_name = s[0] + ''.join(['x' for _ in range(len(s[1]))])
    return folder_name

async def _extract_cve_components(cve_id: str) -> ComponentsOfCveID:
    split_object = cve_id.split('-')
    return ComponentsOfCveID(split_object[0], split_object[1], split_object[2])

