import os
import json
import re
import asyncio
import subprocess
import aiofiles
import time

from dotenv import load_dotenv
from repositories import get_user_repositories
from git_clone_or_pull import clone_or_pull

  
load_dotenv()

def json_serial(obj):
  if isinstance(obj, datetime):
      return obj.__str__()
  raise TypeError ("Type not serializable")

def write_json(data : list,file_name : str):
    os.chdir(os.getenv('DATA_DIRECTORY')) 
    with open(file_name + ".json",mode='a') as f:
         json.dump(data,f,indent=4,default=json_serial)

async def read_file(file_path : str,file_name : str,directory_name : str):
    os.chdir(os.getenv('DATA_DIRECTORY'))
    async with aiofiles.open(file_path,mode='r') as f:
        contents = await f.read()
        result = re.findall(r"#### Reference\n([-\w .\d%@#$\/:'\?;!]+)",contents)
        data_list = []
        if len(result) >= 1 and result[0] != "No PoCs from references.":
            data_list.append({
               "CVE" : file_name,
               "PoC" : result 
                    }
                )
        if data_list:
             write_json(data_list,directory_name)

async def go_to_the_directory(directory_name : str):
    path = os.getenv("PATH_TO_DIRECTORY") + "/" + os.getenv("REPOSITORY_NAME") + "/" + directory_name 
    os.chdir(path)
    tasks = []
    for root,dirs,files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root,file_name)
            task = asyncio.create_task(read_file(file_path,file_name,directory_name))
            tasks.append(task)
    await asyncio.gather(*tasks)


async def main():
    repositories, urls = get_user_repositories()
    clone_or_pull(os.getenv("URL_TO_REPOSITORY"),os.getenv("REPOSITORY_NAME"))
    async with asyncio.TaskGroup() as tg:
        for repo in repositories:
            tg.create_task(go_to_the_directory(repo.name))
        
if __name__ == "__main__":
    asyncio.run(main())
