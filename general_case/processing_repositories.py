import os
from github import Github
from dotenv import load_dotenv


async def processing_repository(user_name : str, repository_name : str):
    #initialize processing
    git = Github(os.getenv("TOKEN"))
    user = git.get_user(user_name)
    repo_init = user.get_repo(repository_name)
    repo_init_second = repo_init.get_contents("")
    #collect all files and subdirs in that directory
    files = [file for file in repo_init_second if file.type == "file"]
    dirs = [directories for directories in repo_init_second if directories.type == "dir"]
    for file in files:
        print(file.name)
    for dir_ in dirs:
        print(dir_.name)
