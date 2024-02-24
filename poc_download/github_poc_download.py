import os
import re

from dotenv import load_dotenv
from typing import List
from file_manager.read_files import read_file_by_path

load_dotenv()

class GithubPOCDownloader:
    def __init__(self):
        self._path_to_poc_directory = os.getenv("PATH_TO_THE_POC_DIRECTORY")
        
    async def traverse_poc_database_and_download():
        for root, dirs, files in os.walk():
            if '.git' in dirs:
                dirs.remove('.git')
            for file in files:
                cve_file_path = os.path.join(root, file)
                data_from_file = await read_file_by_path(cve_file_path)

    
    async def _extract_all_references(data_from_file: str) -> List[str]:
        return re.findall("https:\/\/github.com[a-zA-z0-9@#$ ><?! -\/]+(?=\))", data_from_file)

    async def update_all_knowest_poc_and_download_new_versions():
        ...
    