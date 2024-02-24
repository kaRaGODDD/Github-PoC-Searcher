import asyncio
import os
import re
import subprocess

from typing import List

from dotenv import load_dotenv
from github import Github

from constants_and_other_stuff.structs import RepositoryNameAndUserName
from create_directories.create_directories_on_pc import create_directory_with_help_of_path
from file_manager.read_files import read_file_by_path


load_dotenv()

class GithubPOCDownloader:
    def __init__(self):
        self._path_to_poc_directory = os.getenv("PATH_TO_THE_POC_DIRECTORY")
        self._path_to_the_download_database = os.getenv("POC_DOWNLOAD_DATABASE")
        self._poc_downloader_name = os.getenv("NAME_OF_THE_POC_DATABASE")
        self._poc_directory_name = os.getenv("NAME_OF_THE_POC_DIRECTORY")
        self._github_token = os.getenv("GITHUB_TOKEN")
        self._github_object = Github(self._github_token)

    async def download_files_while_traversing_directory(self):
        for root, dirs, files in os.walk(self._path_to_poc_directory):
            if '.git' in dirs:
                dirs.remove('.git')
            for file in files:
                if file != "README.md":
                    cve_file_path = os.path.join(root, file)
                    cve_file_path_without_extention = cve_file_path.rsplit(".md")[0]
                    data_from_file = await read_file_by_path(cve_file_path)
                    all_github_references = await self._extract_all_references(data_from_file)
                    new_directory_path = await self._replace_old_path_to_new(old_directory_path=cve_file_path_without_extention)
                    await self._processing_with_path_and_refs(all_github_references, new_directory_path)
    
    async def _processing_with_path_and_refs(self, all_github_references: List[str], new_directory_path: str):
        for reference in all_github_references:
            reference_without_prefix = reference.lstrip("https://github.com").split("/")
            if reference_without_prefix:
                user_name_and_repository = RepositoryNameAndUserName(reference_without_prefix[0], reference_without_prefix[1])
                await self._download_repos(user_name_and_repository, new_directory_path) 

    async def _download_repos(self, user_name_and_repository: RepositoryNameAndUserName, new_directory_path: str):
        user = self._github_object.get_user(user_name_and_repository.user_name)
        repository = user.get_repo(user_name_and_repository.repository_name)
        commits_list = repository.get_commits()
        await create_directory_with_help_of_path(new_directory_path)
        version_of_repository = 1
        for commit in commits_list:
            commit_hash = commit.sha
            temp_directory_path = os.path.join(new_directory_path, f"Version_of_repository_{version_of_repository}")
            await create_directory_with_help_of_path(temp_directory_path)
            os.chdir(temp_directory_path)
            subprocess.run(["git", "clone", repository.clone_url, "."])
            subprocess.run(["git", "checkout", commit_hash])   
            version_of_repository += 1  
            

    async def _replace_old_path_to_new(self, old_directory_path: str):
        return re.sub(self._poc_directory_name, self._poc_downloader_name, old_directory_path)
    
    async def _extract_all_references(self, data_from_file: str) -> List[str]:
        return re.findall("https:\/\/github.com[a-zA-z0-9@#$ ><?! -\/]+(?=\))", data_from_file)

    async def update_all_knowest_poc_and_download_new_versions():
        ...

async def main():
    a = GithubPOCDownloader()
    await a.download_files_while_traversing_directory()

asyncio.run(main())
