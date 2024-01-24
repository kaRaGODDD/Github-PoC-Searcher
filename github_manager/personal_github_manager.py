import os
from abc import ABC, abstractmethod
from github import Github
from dotenv import load_dotenv
from constants_and_other_stuff.returning_values import return_github_token

load_dotenv()

class GithubManager(ABC):
    """
    Abstract base class for managing GitHub operations.

    Attributes:
        _github_token (str): GitHub token for authentication.
        _path_to_local_repository (str): Path to the local repository on the computer.
        _user (github.AuthenticatedUser.AuthenticatedUser): GitHub user object.
    """

    def __init__(self, github_token: str, path_to_local_repository_on_pc: str):
        """
        Initialize the GitHub manager.

        Args:
            github_token (str): GitHub token.
            path_to_local_repository_on_pc (str): Path to the local repository on the computer.
        """
        self._github_token = github_token
        self._path_to_local_repository = path_to_local_repository_on_pc
        self._user = self._get_user()

    def _get_user(self):
        """
        Get the GitHub user object.

        Returns:
            github.AuthenticatedUser.AuthenticatedUser: GitHub user object.
        """
        return Github(self._github_token).get_user()

    def _get_local_repository_path(self):
        """
        Get the path to the local repository.

        Returns:
            str: Path to the local repository.
        """
        return self._path_to_local_repository

    @abstractmethod
    async def create_repository(self, name_of_the_repository: str):
        """
        Abstract method for creating a repository on GitHub.

        Args:
            name_of_the_repository (str): Name of the repository to be created.
        """
        ...

    @abstractmethod
    async def make_a_commit(self, commit_message: str):
        """
        Abstract method for creating and pushing a commit to the repository.

        Args:
            commit_message (str): Commit message.
        """
        ...

    @abstractmethod
    async def update_database(self):
        """
        Abstract method for updating the database.
        """
        ...
