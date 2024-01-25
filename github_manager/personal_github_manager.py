import os
from abc import ABC, abstractmethod
from github import Github
from git import Repo
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

    def __init__(self):
        """
        Initialize the GitHub manager.
        """
        self._github_token = os.getenv("GITHUB_TOKEN")
        self._path_to_local_repository = os.getenv("PATH_TO_THE_DATA_DIRECTORY")
        self._user = Github(self._github_token).get_user()

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
    async def add_in_index(self):
        """
        Abstract method to add changes to the index in preparation for a commit.
        """
        ...

    @abstractmethod
    async def update_database(self):
        """
        Abstract method for updating the database.
        """
        ...
