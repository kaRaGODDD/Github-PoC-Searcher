import aiofiles
import os
import re

from dotenv import load_dotenv
from constants_and_other_stuff.pydantic_models import CveExploit

load_dotenv()

async def distribute_cve_object(cve_object: CveExploit):
    await _parse_cve_object_by_year(cve_object)
    await _parse_cve_object_by_id(cve_object)

async def _parse_cve_object_by_year(cve_object: CveExploit):
    pass

async def _parse_cve_object_by_id(cve_object: CveExploit):
    pass