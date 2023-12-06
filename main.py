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
from increasing_file_descriptors import incr_file_descriptors

load_dotenv()

async def write_json(data: dict, file_name : str):
    os.chdir(os.getenv('DATA_DIRECTORY'))
    async with aiofiles.open(f"{file_name}.json", 'a') as f:
        await f.write(json.dumps(data,indent=4,ensure_ascii=False))

async def write_json_for_url_lst(data: dict, file_name : str):
    os.chdir(os.getenv('DATA_DIRECTORY'))
    async with aiofiles.open(f"{file_name}.json", 'w') as f:
        await f.write(json.dumps(data,indent=4,ensure_ascii=False))


async def read_json(file_name : str):
    data_directory = os.getenv('DATA_DIRECTORY')
    file_path = os.path.join(data_directory, f"{file_name}.json")
    if os.path.isfile(file_path):
        if os.path.getsize(file_path) == 0:
            return {}
        else:
            async with aiofiles.open(file_path, 'r') as f:
                data = json.loads(await f.read())
            return data
    else:
        return {}

async def new_version(directory_name : str,flag = False):
    path = os.getenv("PATH_TO_DIRECTORY") + "/" + os.getenv("REPOSITORY_NAME") + "/" + directory_name
    indicator = False
    if flag:
        data = await read_json(directory_name)
        fresh_data = {}
        new_data_for_second_write = {}
    else:
        data = {}
    for root,dirs,files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root,file_name)
            data_directory = os.getenv('DATA_DIRECTORY')
            async with aiofiles.open(file_path,mode='r') as f:
                contents = await f.read()
                result = re.findall(r"#### Reference\n(- https?[\w:/.+a-z0-9-= \n @( )]+)",contents)
                result = [url.replace("\n",'') for url in result]
                if len(result) >= 1 and result[0] != "No PoCs from references.":
                    result = [url.replace("\n",'') for url in result]
                    urls = result[0].split('- ')
                    urls = [url for url in urls if url.startswith("http")]
                    if flag:
                        new_data_for_second_write[file_name] = urls
                        if data.get(file_name,"Not find") == "Not find":
                            fresh_data[file_name] = urls
                            print(file_name)
                        elif len(data.get(file_name)) < len(urls):
                            indicator = True
                            print(urls)
                    else:
                        data[file_name] = urls
        if flag:
            if indicator and new_data_for_second_write:
                await write_json_for_url_lst(new_data_for_second_write,directory_name)
            else:
                if fresh_data:
                    await write_json(fresh_data,directory_name)
        else:
            if data:
                await write_json(data,directory_name)

async def check_for_update(path_to_the_directory : str):
    if os.path.exists(path_to_the_directory):
        await incr_file_descriptors()
        clone_or_pull(os.getenv("URL_TO_REPOSITORY"),os.getenv("REPOSITORY_NAME"))
        repositories, urls = get_user_repositories()
        async with asyncio.TaskGroup() as tg:
            for repo in repositories:
                tg.create_task(new_version(repo.name,True))
    else:
        await incr_file_descriptors()
        subprocess.call(['mkdir',os.getenv("DIRECTORY_NAME_FOR_STORE_THE_DATA")])
        repositories, urls = get_user_repositories()
        clone_or_pull(os.getenv("URL_TO_REPOSITORY"),os.getenv("REPOSITORY_NAME"))
        async with asyncio.TaskGroup() as tg:
            for repo in repositories:
                tg.create_task(new_version(repo.name))

async def main():
   await check_for_update(os.getenv("DIRECTORY_NAME_FOR_STORE_THE_DATA"))


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
