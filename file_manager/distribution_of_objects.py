import aiofiles
import os
import re

import math
from dotenv import load_dotenv
from constants_and_other_stuff.pydantic_models import CveExploit
from constants_and_other_stuff.constants import pattern_of_md_file

load_dotenv()

async def distribute_cve_object(cve_object: CveExploit):
    await _parse_cve_object_by_year(cve_object)
    await _parse_cve_object_by_id(cve_object)

async def _parse_cve_object_by_year(cve_object: CveExploit):
    pass    

async def _parse_cve_object_by_id(cve_object: CveExploit):
    determine_folder_name_by_formula = await _determine_folder_name(cve_object.id)

async def _determine_folder_name(cve_obj_id: str):
    s = str(int(cve_obj_id.split("-")[2]) / 1000).split(".")
    folder_name = s[0]
    for i in range (0,len(s[1])):
        folder_name += "x"
    return folder_name
