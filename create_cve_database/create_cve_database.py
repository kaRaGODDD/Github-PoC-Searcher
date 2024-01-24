from github_manager.personal_github_manager import GithubManager
from git import Repo

class CreateCveDatabase(GithubManager):
    async def create_repository(self, name_of_the_repository: str, private: bool = True):
        """
        Create a GitHub repository with the specified name.

        Args:
            name_of_the_repository (str): The name of the repository to be created.
            private (bool, optional): If True, create a private repository. 
                                      If False, create a public repository. Default is True.
        """
        self._user.create_repo(name_of_the_repository, private=private)

    async def add_in_index(self, all: bool = True):
        """
        Add changes to the Git index in preparation for a commit.

        Args:
            all (bool, optional): If True, add all changes to the index. 
                                  If False, only add modified and new files. Default is True.
        """
        self._repo.index.add(all=all)

    async def make_a_commit(self, commit_message: str):
        """
        Create a Git commit with the specified commit message.

        Args:
            commit_message (str): The message for the commit.
        """
        self._repo.index.commit(commit_message)

    async def push_changes_to_server(self):
        """Push local changes to the remote repository on GitHub."""
        try:
            origin = self._repo.create_remote('origin', self._repository.clone_url)
        except Exception as e:
            # If remote repository already exists, get it
            origin = self._repo.remote('origin')
        try:
            origin.push('dev')
        except Exception as e:
            print("Error pushing changes:", e)

    async def update_database(self):
        """Update the database (placeholder for the actual implementation)."""
        pass
