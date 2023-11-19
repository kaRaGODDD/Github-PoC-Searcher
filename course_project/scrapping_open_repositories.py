from github import Github
from datetime import datetime
import os
import json
import base64
import requests

from dotenv import load_dotenv

load_dotenv()

import re
import asyncio
import aiofiles
import itertools
import time

start = time.time()

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.__str__()
    raise TypeError ("Type not serializable")

async def write_json(data : list, filename):
    async with aiofiles.open(filename, 'a') as f:
        await f.write(json.dumps(data,indent=4,default=json_serial))

async def parse_each_file_async(file,exploits_repository,repository_name : str,user_name : str,i):
        
        print(f"task{i}")
        parse_date = datetime.now().replace(microsecond=0)
        commits = list(exploits_repository.get_commits(path=file.path))
        data_list = []

        if commits:
            
            file_name = file.path
            
            first_commit = commits[-1].commit.committer.date.strftime('%d-%m-%Y %H:%M:%S') 
            author_of_first_commit = commits[-1].commit.committer.name
             
            author_of_last_commit = commits[0].commit.committer.name
            last_commit = commits[0].commit.committer.date.strftime('%d-%m-%Y %H:%M:%S')
             
            decoded = base64.b64decode(file.content).decode('utf-8')
            
            result = re.findall("(\(https?:\/\/[\w.\/-\?-&%'^#@)]+)",decoded)#cve exploit ref
            result1 = re.search("Description\n\n[\w\s,.]+",decoded)
            result3 = re.findall("#### Github\n((- https?:\/[\w.>?@#*&\/-0-9]+)|[\w .]+)",decoded)

            if result1: 
                description = result1[0].strip().replace("Description\n\n",'')#получение описания
            else:
                description = "This file doesn`t have description"
            
            result3_str = [list(t) for t in result3]
            resulted = list(itertools.chain(*result3_str)) #получение github ссылок в список

            data_list.append(
                {
                   f"{user_name}/cve scrapping date" : parse_date, 
                   "File name" : file_name,
                   "First Commit" : first_commit,
                   "Author of first commit" : author_of_first_commit,
                   "Last Commit" :  last_commit,
                   "Author of last commit" : author_of_last_commit,
                   "Inside information of file" : {
                            "Description" : description,
                            "Github references" : resulted,
                            "CVE references" : result
                       }
                }
            )
            await write_json(data_list,f"{repository_name}.json")
        
     


async def parse_trickvest():
    
    user_name = "trickest"
    github_token = ''
    from_github = Github(github_token)
    
    tricket_user = from_github.get_user(user_name)
    exploits_repository = tricket_user.get_repo("cve")
     
    repository_of_2023_exploits = exploits_repository.get_contents("2023")
    
    #Получаю все файлы в этом репозитории: Их название first commit, last commit, author
    files = [file for file in repository_of_2023_exploits if file.type == "file"]
    i = 0
    #task_list = []
    #for file in files:
        #task1 = asyncio.create_task(parse_each_file_async(file,exploits_repository,"2023",f"{user_name}",i))
        #task_list.append(task1)

    #await asyncio.gather(*task_list)
    async with asyncio.TaskGroup() as tg:
        for file in files:
            tg.create_task(parse_each_file_async(file,exploits_repository,"2023",f"{user_name}",i))
            i +=1 


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(parse_trickvest())

if __name__ == "__main__":
    asyncio.run(main())
    end = time.time()-start
    print(end)
    
