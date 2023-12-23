import os
import asyncio

from github import Github
from dotenv import load_dotenv

from download_decoded_file_and_dirs import write_file
from download_decoded_file_and_dirs import write_directory
from create_directories import create_directory_by_user_name

load_dotenv()

black_list = ["LICENSE",".gitignore"]

async def processing_repository(user_name : str, repository_name : str):
    #TODO rewrite it to exception 
    token = os.getenv('GITHUB_TOKEN')
    git = Github(token)
    user = git.get_user(user_name)
    just_repo = user.get_repo(repository_name)
    if just_repo.size:
        repo_content = just_repo.get_contents("/")
        if not repo_content:
            print(f"No files in repository {repository_name}")
            return
        files = [file for file in repo_content if file.type == "file" and file.name not in black_list]
        dirs = [dirs for dirs in repo_content if dirs.type == "dir"]
        if not files:
            print(f"No files to download in repository {repository_name}")
            return
        await create_directory_by_user_name(user_name)
        for file in files:
            if file.name not in black_list and file.size > 0:
                await write_file(file.download_url,file.name,user_name)
        if dirs:
            for directory in dirs:
                await write_directory(user_name,directory.name,just_repo)
