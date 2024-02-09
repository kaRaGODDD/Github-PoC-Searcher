import os
from dotenv import load_dotenv

from constants_and_other_stuff.enums import POCSearchMethod
from constants_and_other_stuff.structs import CveIDComponents, POCModel

from create_directories.create_directories_on_pc import create_directory

from file_manager.distribution_of_objects import _generate_folder_name, _extract_cve_components
from file_manager.write_file_by_poc_pattern import write_poc


load_dotenv()

async def process_of_distribute_poc(cve_id: str, poc_object: POCModel, search_choice: POCSearchMethod):
    split_data = await _extract_cve_components(cve_id)
    await _create_yearly_directories(split_data)
    path = await _create_id_based_directory(split_data)
    await write_poc(cve_id,poc_object,path, search_choice)

async def _create_yearly_directories(cve_object: CveIDComponents):
    await create_directory(os.getenv("NAME_OF_THE_POC_DIRECTORY"), os.getenv("PATH_TO_THE_BASE_DIRECTORY"))
    await create_directory(cve_object.cve_year, os.getenv("PATH_TO_THE_POC_DIRECTORY"))

async def _create_id_based_directory(cve_object: CveIDComponents) -> str:
    determine_folder_name_by_formula = await _generate_folder_name(cve_object)
    full_path = os.path.join(os.getenv("PATH_TO_THE_POC_DIRECTORY"), cve_object.cve_year)
    await create_directory(determine_folder_name_by_formula, full_path)
    return os.path.join(full_path,determine_folder_name_by_formula)
