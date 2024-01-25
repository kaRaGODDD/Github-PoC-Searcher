import asyncio
import os
import subprocess

from datetime import datetime
from dotenv import load_dotenv
from git import Repo
from github_manager.personal_github_manager import GithubManager
from scrapping_nvd_database.scrapping_nvd_database import NvdDataBaseScrapper

load_dotenv()

class CreateCveDatabase(GithubManager):
    def set_repository_name(self, name_of_the_repository: str):
        """Set the name of the repository."""
        self._name_of_the_repository = name_of_the_repository

    def set_user_login(self, user_login: str):
        """Set the user login."""
        self._user_login = user_login

    def set_repository_instance(self, private: bool = True):
        """Create a GitHub repository instance."""
        self._repository = self._user.create_repo(self._name_of_the_repository, private=private)

    async def create_repository(self, name_of_the_repository: str, private: bool=True):
        """
        Create a GitHub repository with the specified name.

        Args:
            name_of_the_repository (str): The name of the repository to be created.
            private (bool, optional): If True, create a private repository. 
                                      If False, create a public repository. Default is True.
        """
        try:
            self.set_repository_name(name_of_the_repository)
            self.set_user_login(self._user.login)
            self.set_repository_instance(private)
        except Exception as e:
            e.add_note(f"Repository {name_of_the_repository} already created")

    async def add_in_index(self):
        """Add changes to the Git index in preparation for a commit."""
        os.chdir(self._path_to_local_repository)
        subprocess.run(["git", "add", "."])

    async def make_a_commit(self, commit_message: str):
        """Create a Git commit with the specified commit message."""
        subprocess.run(["git", "commit", "-m", commit_message])

    async def push_changes_to_server(self):
        """Push local changes to the remote repository on GitHub."""
        try:
            origin = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode().strip()
        except subprocess.CalledProcessError:
            subprocess.run(["git", "remote", "add", "origin", self._repository.clone_url])
            origin = self._repository.clone_url

        try:
            subprocess.run(["git", "push", "-u", "origin", "dev"])
        except subprocess.CalledProcessError as e:
            print(f"Error pushing changes to 'dev': {e}")

    async def update_database(self, rewrite_last_date: bool=True):
        """Update the database."""
        nvd_instance = NvdDataBaseScrapper()
        await nvd_instance.update(rewrite_last_date)
        await self.add_in_index() 
        await self.make_a_commit(f"Autoupdate {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await self.push_changes_to_server()
