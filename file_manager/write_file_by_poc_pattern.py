import os
import aiofiles
from dotenv import load_dotenv
from constants_and_other_stuff.structs import CveModelForPoC, CvePoc
from constants_and_other_stuff.constants import pattern_of_md_poc_file
from constants_and_other_stuff.enums import POCChoiceSearch
from constants_and_other_stuff.pydantic_models import GraphQLAnswerModel

load_dotenv()

async def write_poc(cve_id: str, poc_object: CveModelForPoC, path: str,search_choice: POCChoiceSearch):
    where_to_write = os.path.join(path, f"{cve_id}.md")
    ready_poc_object = await _return_ready_poc_object(cve_id,poc_object,search_choice)
    
    async with aiofiles.open(where_to_write, "w", encoding='utf-8') as f:
        await f.write(pattern_of_md_poc_file.format(
            ready_poc_object.cve_id,
            ready_poc_object.description,
            ready_poc_object.formatted_references
        ))

async def _return_ready_poc_object(cve_id: str, cve_model: CveModelForPoC,search_choice: POCChoiceSearch) -> CvePoc:
    description = cve_model.description[0].strip("[]'") if cve_model.description and cve_model.description[0] else ""
    match search_choice:
        case POCChoiceSearch.GITHUB_API_SEARCH:
            references_formatted = "\n".join([f'- ["Follow the link"]({ref["url"]})' for ref in cve_model.github_urls]) if cve_model.github_urls else ""
        case POCChoiceSearch.GRAPHQL_SEARCH:
            references_formatted = "\n".join([f'- ["Follow the link"]({ref.node.url})' for ref in cve_model.github_urls]) if cve_model.github_urls else ""
    return CvePoc(cve_id, description, references_formatted)
