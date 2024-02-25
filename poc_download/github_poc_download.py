import asyncio
import os
import re
import subprocess
import tempfile

from datetime import datetime
from typing import List

from dotenv import load_dotenv
from github import Github

from constants_and_other_stuff.structs import RepositoryNameAndUserName
from create_directories.create_directories_on_pc import create_directory_with_help_of_path
from file_manager.read_files import read_file_by_path


load_dotenv()

class GithubPOCDownloader:
    def __init__(self):
        self._path_to_the_poc_directory = os.getenv("PATH_TO_THE_POC_DIRECTORY")
        self._path_to_the_download_database = os.getenv("POC_DOWNLOAD_DATABASE")
        self._poc_downloader_name = os.getenv("NAME_OF_THE_POC_DATABASE")
        self._poc_directory_name = os.getenv("NAME_OF_THE_POC_DIRECTORY")
        self._github_token = os.getenv("GITHUB_TOKEN")
        self._github_object = Github(self._github_token)
        self._poc_year_directory = os.getenv("PATH_TO_POC_YEAR_DIRECTORY")

    async def start_download(self):
        try:
            await self._download_multiple_directories()
        except Exception as e:
            print(f"Error during download: {e}")

    async def _download_multiple_directories(self):
        tasks = [
            self._download_files_while_traversing_directory_consistently(self._poc_year_directory.format(year))
            for year in range(1999, datetime.now().year + 1)
        ]
        await asyncio.gather(*tasks)

    async def _download_files_while_traversing_directory_consistently(self, path: str):
        try:
            for root, dirs, files in os.walk(path):
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
        except Exception as e:
            print(f"Error during file traversal: {e}")

    async def _processing_with_path_and_refs(self, all_github_references: List[str], new_directory_path: str):
        try:
            for reference in all_github_references:
                reference_without_prefix = reference.lstrip("https://github.com").split("/")
                if reference_without_prefix:
                    user_name_and_repository = RepositoryNameAndUserName(reference_without_prefix[0], reference_without_prefix[1])
                    await self._download_repos_with_compression(user_name_and_repository, new_directory_path)
        except Exception as e:
            print(f"Error during processing references: {e}")

    async def _download_repos_with_compression(self, user_name_and_repository: RepositoryNameAndUserName, new_directory_path: str):
        try:
            user = self._github_object.get_user(user_name_and_repository.user_name)
            repository = user.get_repo(user_name_and_repository.repository_name)
            commits_list = repository.get_commits()
            await create_directory_with_help_of_path(new_directory_path)
            version_of_repository = 1
            for commit in commits_list:
                commit_hash = commit.sha
                archive_filename = f"Version_of_repository_{version_of_repository}.zip"
                archive_path = os.path.join(new_directory_path, archive_filename)
                temp_clone_dir = tempfile.mkdtemp()
                os.chdir(temp_clone_dir)
                subprocess.run(["git", "clone", repository.clone_url, "."])
                subprocess.run(["git", "archive", "-o", archive_path, commit_hash])
                version_of_repository += 1
        except Exception as e:
            print(f"Error during repository download: {e}")

    async def _replace_old_path_to_new(self, old_directory_path: str):
        try:
            return re.sub(self._poc_directory_name, self._poc_downloader_name, old_directory_path)
        except Exception as e:
            print(f"Error during path replacement: {e}")

    async def _extract_all_references(self, data_from_file: str) -> List[str]:
        try:
            return re.findall("https:\/\/github.com[a-zA-z0-9@#$ ><?! -\/]+(?=\))", data_from_file)
        except Exception as e:
            print(f"Error during references extraction: {e}")

    async def update_all_knowest_poc_and_download_new_versions():
        ...


async def main():
    a = GithubPOCDownloader()
    await a.start_download()

asyncio.run(main())
