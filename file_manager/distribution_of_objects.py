import asyncio
import aiofiles
import os
import math

from dotenv import load_dotenv
from typing import Optional

from constants_and_other_stuff.enums import FileFormat, DirectoryType
from constants_and_other_stuff.structs import CveIDComponents
from constants_and_other_stuff.pydantic_models import CveExploit

from create_directories.create_directories_on_pc import create_directory
from file_manager.write_file import write_file_by_cve_template, write_file_by_json


load_dotenv()

async def return_location_of_cve_object(string_cve_object: str, type_of_the_directory: DirectoryType) -> Optional[str]:
    data_about_cve = await _extract_cve_components(string_cve_object)  
    path_to_cve_object = await _by_type_of_directory_determine_path(type_of_the_directory, data_about_cve)
    return os.path.join(path_to_cve_object, string_cve_object) + ".md"            

async def _by_type_of_directory_determine_path(type_of_the_directory: DirectoryType, data_about_cve: CveIDComponents):
    match type_of_the_directory:
        case DirectoryType.POC_DIRECTORY:
            path_determined_by_type_of_directory = await _get_directory_path_for_type(data_about_cve.cve_year, type_of_the_directory)
            path_to_cve_object = await _get_directory_path_for_cve_object(data_about_cve, path_determined_by_type_of_directory)
        case DirectoryType.CVE_DATABASE_DIRECTORY:
            path_determined_by_type_of_directory = await _get_directory_path_for_type(data_about_cve.cve_year, type_of_the_directory)
            path_to_cve_object = await _get_directory_path_for_cve_object(data_about_cve, path_determined_by_type_of_directory)
    return path_to_cve_object

async def _get_directory_path_for_type(cve_year: int, type_of_the_directory: DirectoryType) -> str:
    match type_of_the_directory:
        case DirectoryType.CVE_DATABASE_DIRECTORY:
            return os.path.join(os.getenv("PATH_TO_THE_DATA_DIRECTORY"), cve_year)
        case DirectoryType.POC_DIRECTORY:
            return os.path.join(os.getenv("PATH_TO_THE_POC_DIRECTORY"), cve_year)

async def _get_directory_path_for_cve_object(cve_object:  CveIDComponents, path_to_cve_object: str) -> str:
    determine_folder_name_by_formula = await _generate_folder_name(cve_object)
    path = os.path.join(path_to_cve_object, determine_folder_name_by_formula)
    if not os.path.exists(path):
        await create_directory(determine_folder_name_by_formula, path_to_cve_object)
    return path

async def process_and_distribute_cve(cve_object: CveExploit, file_format: FileFormat, json_answer: Optional[dict]={}):
    components_of_the_cve = await _extract_cve_components(cve_object.id)
    match file_format:
        case FileFormat.MD:
            await _create_yearly_directories(components_of_the_cve, file_format)
            path = await _create_id_based_directory(components_of_the_cve)
            await write_file_by_cve_template(cve_object, path)
        case FileFormat.JSON:
            await _create_yearly_directories(components_of_the_cve, file_format)
            path = await _create_id_based_directory(components_of_the_cve, file_format)
            await write_file_by_json(cve_object.id, json_answer, path)

async def _create_yearly_directories(cve_object: CveIDComponents, file_saving: FileFormat):
    match file_saving:
        case FileFormat.MD:
            await create_directory(os.getenv("NAME_OF_THE_DATA_DIRECTORY"), os.getenv("PATH_TO_THE_BASE_DIRECTORY"))
            await create_directory(cve_object.cve_year, os.getenv("PATH_TO_THE_DATA_DIRECTORY"))
        case FileFormat.JSON:
            await create_directory(os.getenv("NAME_OF_THE_DATA_DIRECTORY"), os.getenv("PATH_TO_THE_BASE_DIRECTORY"))
            await create_directory(os.getenv("NAME_OF_THE_JSON_AWSWERS_DIRECTORY"),os.getenv("PATH_TO_THE_DATA_DIRECTORY"))
            await create_directory(cve_object.cve_year,os.getenv("PATH_TO_THE_JSON_ANSWERS_DIRECTORY"))
            
async def _create_id_based_directory(cve_object: CveIDComponents, file_format: FileFormat = FileFormat.MD) -> str:
    determine_folder_name_by_formula = await _generate_folder_name(cve_object)
    match file_format:
        case FileFormat.MD:
            full_path = os.path.join(os.getenv("PATH_TO_THE_DATA_DIRECTORY"), cve_object.cve_year)
        case FileFormat.JSON:
            full_path = os.path.join(os.getenv("PATH_TO_THE_JSON_ANSWERS_DIRECTORY"), cve_object.cve_year)
    await create_directory(determine_folder_name_by_formula, full_path)
    return os.path.join(full_path,determine_folder_name_by_formula)

async def _generate_folder_name(cve_obj: CveIDComponents):
    rational_number = str((int(cve_obj.cve_id) / 1000)).split(".")
    folder_name = rational_number[0] + ''.join(['x' for _ in range(max(len(rational_number[1]),3))])
    return folder_name

async def _extract_cve_components(cve_id: str) -> CveIDComponents:
    split_object = cve_id.split('-')
    print(cve_id)
    return CveIDComponents(split_object[0], split_object[1], split_object[2])
