import aiofiles
import os

from dotenv import load_dotenv

from constants_and_other_stuff.constants import pattern_of_md_file
from constants_and_other_stuff.pydantic_models import CveExploit

load_dotenv()

async def write_file_by_pattern(ready_cve_object: CveExploit, path: str):
    where_to_write = os.path.join(path, f"{ready_cve_object.id}.md")
    references_formatted = "\n".join([f'- **{ref.source}**: {ref.url}' for ref in ready_cve_object.references]) if ready_cve_object.references else ""
    
    async with aiofiles.open(where_to_write, 'w') as f:
        await f.write(pattern_of_md_file.format(
            ready_cve_object.id,
            ready_cve_object.references[0].url if ready_cve_object.references else "",
            ready_cve_object.descriptions[0].value if ready_cve_object.descriptions else "",
            ready_cve_object.metrics.cvssMetricV2[0].cvssData.accessVector if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].cvssData.baseScore if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].exploitabilityScore if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].impactScore if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].baseSeverity if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.published,
            ready_cve_object.vulnStatus,
            references_formatted
        ))