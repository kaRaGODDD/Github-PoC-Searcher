import os
import aiofiles

from dotenv import load_dotenv

from constants_and_other_stuff.structs import POCModel, POCData, POCObject
from constants_and_other_stuff.constants import POC_FILE_TEMPLATE, MITRE_URL
from constants_and_other_stuff.enums import POCSearchMethod
from constants_and_other_stuff.pydantic_models import GraphQLAnswerModel


load_dotenv()

async def write_poc(cve_id: str, poc_object: POCModel, path: str,search_choice: POCSearchMethod):
    where_to_write = os.path.join(path, f"{cve_id}.md")
    ready_poc_object = await _return_ready_poc_object(cve_id, poc_object, search_choice)
    
    async with aiofiles.open(where_to_write, "w", encoding='utf-8') as f:
        await f.write(POC_FILE_TEMPLATE.format(
            ready_poc_object.cve_id,
            MITRE_URL.format(cve_id),
            f"- `{ready_poc_object.description}`",
            ready_poc_object.formatted_references
        ))

async def write_poc_with_full_path(cve_id: str, poc_object: POCModel, full_path: str,search_choice: POCSearchMethod):
    ready_poc_object = await _return_ready_poc_object(cve_id, poc_object, search_choice)
    
    async with aiofiles.open(full_path, "w", encoding='utf-8') as f:
        await f.write(POC_FILE_TEMPLATE.format(
            ready_poc_object.cve_id,
            MITRE_URL.format(cve_id),
            f"- `{ready_poc_object.description}`",
            ready_poc_object.formatted_references
        ))

async def write_new_poc_object(cve_id: str, new_poc_object: POCObject, path_to_the_new_poc_object: str):
    print(f"Path to new poc object {path_to_the_new_poc_object}")
    async with aiofiles.open(path_to_the_new_poc_object, "w", encoding='utf-8') as f:
        await f.write(POC_FILE_TEMPLATE.format(
            cve_id,
            MITRE_URL.format(cve_id),
            f"- `{new_poc_object.description}`",
            f'- ["Follow the link"]({new_poc_object.github_url})'
        ))

async def _return_ready_poc_object(cve_id: str, cve_model: POCModel,search_choice: POCSearchMethod) -> POCData:
    description = cve_model.description[0].strip("[]'") if cve_model.description and cve_model.description[0] else ""
    match search_choice:
        case POCSearchMethod.GITHUB_API_SEARCH: #{ref["url"]})
            references_formatted = "\n".join([f'- ["Follow the link"]({ref})' for ref in cve_model.github_urls if ref != MITRE_URL]) if cve_model.github_urls else ""
        case POCSearchMethod.GRAPHQL_SEARCH:
            references_formatted = "\n".join([f'- ["Follow the link"]({ref.node.url})' for ref in cve_model.github_urls if ref.node.url != MITRE_URL]) if cve_model.github_urls else ""
    return POCData(cve_id, description, references_formatted)
