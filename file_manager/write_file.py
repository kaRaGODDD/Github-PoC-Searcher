import asyncio
import aiofiles
import os

from dotenv import load_dotenv

from constants_and_other_stuff.constants import pattern_of_md_file
from constants_and_other_stuff.structs import CvePattern

load_dotenv()

async def write_file_by_pattern(ready_cve_object: CvePattern):
    async with aiofiles.open(f"{ready_cve_object.cve_id}.md", 'w') as f:
        await f.write(pattern_of_md_file.format(
            ready_cve_object.cve_id,
            ready_cve_object.url,
            ready_cve_object.description,
            ready_cve_object.access_vector,
            ready_cve_object.base_score,
            ready_cve_object.exploitability_score,
            ready_cve_object.impact_score,
            ready_cve_object.base_severity,
            ready_cve_object.published_date,
            ready_cve_object.vulnerability_status,
            ready_cve_object.references
        ))
