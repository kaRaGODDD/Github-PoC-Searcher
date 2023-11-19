from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

def get_user_repositories() -> tuple:
   
    git = Github(os.getenv("GITHUB_TOKEN"))
    user_name = os.getenv("USER_NAME")
    user = git.get_user(user_name)
    repo = user.get_repo(os.getenv("REPOSITORY_NAME")) 
    
    contents = repo.get_contents("")
    repositories = [content for content in contents if content.type == "dir"]
    repositories_urls = [content.html_url for content in contents if content.type == "dir"]
    repositories.pop()
    repositories_urls.pop()

    return (repositories,repositories_urls)
