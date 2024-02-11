import aiofiles
import os
import json

from datetime import datetime
from dotenv import load_dotenv

from constants_and_other_stuff.constants import CVE_FILE_TEMPLATE, MITRE_URL
from constants_and_other_stuff.pydantic_models import CveExploit


load_dotenv()

async def write_file_by_cve_template(ready_cve_object: CveExploit, path: str):
    where_to_write = os.path.join(path, f"{ready_cve_object.id}.md")
    references_formatted = "\n".join([f'- **{ref.source}**: {ref.url}' for ref in ready_cve_object.references]) if ready_cve_object.references else ""
    publish_date_formatted = datetime.fromisoformat(ready_cve_object.published).strftime('%Y-%m-%d %H:%M:%S')

    async with aiofiles.open(where_to_write, 'w', encoding='utf-8') as f:
        await f.write(CVE_FILE_TEMPLATE.format(
            ready_cve_object.id,
            MITRE_URL.format(ready_cve_object.id),
            ready_cve_object.descriptions[0].value.replace("\n", "").strip() if ready_cve_object.descriptions else "",
            ready_cve_object.metrics.cvssMetricV2[0].cvssData.accessVector if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].cvssData.baseScore if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].exploitabilityScore if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].impactScore if ready_cve_object.metrics.cvssMetricV2 else "",
            ready_cve_object.metrics.cvssMetricV2[0].baseSeverity if ready_cve_object.metrics.cvssMetricV2 else "",
            publish_date_formatted,
            ready_cve_object.vulnStatus,
            references_formatted
        ))
    #TODO: replace that to logging/loguru
    print(f"That object {ready_cve_object.id} was written")

async def write_file_by_json(ready_cve_object_id: str, json_answer: dict, path: str):
    where_to_write = os.path.join(path, f"{ready_cve_object_id}.json")
    async with aiofiles.open(where_to_write, "w", encoding='utf-8') as f:
        json_string = json.dumps(json_answer, indent=4)
        await f.write(json_string)
        