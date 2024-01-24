from github_manager.personal_github_manager import GithubManager

class CveDataBase(GithubManager):
    async def create_repository(self, name_of_the_repository: str,private: bool = True): 
        ...

    async def make_a_commit(self, commit_message: str):
        ...         
    
    async def update_database():
        ...
