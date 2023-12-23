import github
import aiofiles
import asyncio
import aiohttp
import os

from create_directories import just_create_folder

async def write_file(download_url : str,file_name : str,user_name : str,name_of_the_directory = None):
    await asyncio.to_thread(os.chdir, os.getenv('PATH_TO_THE_DATA_DIRECTORY'))
    await asyncio.to_thread(os.chdir, user_name)
    if name_of_the_directory:
        await asyncio.to_thread(os.chdir,name_of_the_directory)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url,timeout=30) as response:
                async with aiofiles.open(file_name,mode="wb") as f:
                    await f.write(await response.read())
    except asyncio.TimeoutError:
        print("Timeout occurred while downloading the file.")

async def write_directory(user_name : str, name_of_the_directory : str, repository_object, repository_previous_name=""):
    if await asyncio.to_thread(os.path.exists,os.getenv('PATH_TO_THE_DATA_DIRECTORY')):
        await asyncio.to_thread(os.chdir,os.getenv('PATH_TO_THE_DATA_DIRECTORY'))
        await asyncio.to_thread(os.chdir,user_name)
    if not await asyncio.to_thread(os.path.exists,name_of_the_directory):
        await just_create_folder(name_of_the_directory,user_name)
        await asyncio.to_thread(os.chdir,name_of_the_directory)
    if repository_previous_name == "":
        repository_previous_name = name_of_the_directory
        repository_query = repository_object.get_contents(repository_previous_name)
        repository_previous_name += "/"
    else:
        repository_previous_name += name_of_the_directory
        repository_query = repository_object.get_contents(repository_previous_name)
        repository_previous_name += "/"
    files = [file for file in repository_query if file.type == "file"]
    directories = [directory for directory in repository_query if directory.type == "dir"]
    if files:
        for file in files:
            await write_file(file.download_url,file.name,user_name,name_of_the_directory)
    if directories:
        for directory in directories:
            await write_directory(user_name,directory.name,repository_object,repository_previous_name)

