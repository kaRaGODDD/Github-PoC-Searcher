import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

def clone_or_pull(url : str, name_of_repository : str):
    if os.path.exists(os.getenv('PATH_TO_DIRECTORY')+'/'+name_of_repository):
        os.chdir(os.getenv('PATH_TO_DIRECTORY')+'/'+name_of_repository)
        subprocess.run(['git', 'pull'])
    else:
        os.chdir(os.getenv('PATH_TO_DIRECTORY'))
        subprocess.run(['git', 'clone', url+".git"])

