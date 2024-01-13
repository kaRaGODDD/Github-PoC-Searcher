import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def create_directory_on_pc(name_of_the_directory: str):
    if await asyncio.to_thread(os.path.exists,os.path.join(os.getenv("PATH_TO_THE_DATA_DIRECTORY"),name_of_the_directory)):
        print("EXIST")
    else:
        data_dir = await asyncio.to_thread(os.getenv,"PATH_TO_THE_DATA_DIRECTORY")
        await asyncio.to_thread(os.chdir, data_dir)
        await asyncio.to_thread(os.makedirs, name_of_the_directory)

async def create_data_directory():
    if await asyncio.to_thread(os.path.exists,os.getenv(('PATH_TO_THE_DATA_DIRECTORY'))):
        print("EXISTS")
    else:
        await asyncio.to_thread(os.chdir,os.getenv("PATH_TO_THE_BASE_DIR"))
        await asyncio.to_thread(os.makedirs,os.getenv("NAME_OF_THE_DATA_DIRECTORY"))

async def create_directory_by_user_name(name_of_the_directory : str):
    base_dir = os.getenv("PATH_TO_THE_BASE_DIR")
    data_dir = os.getenv('PATH_TO_THE_DATA_DIRECTORY')
    data_directory_name = os.getenv('NAME_OF_THE_DATA_DIRECTORY')

    if await asyncio.to_thread(os.path.exists, data_dir):
        await asyncio.to_thread(os.chdir, data_dir)
        await asyncio.to_thread(os.makedirs, name_of_the_directory, exist_ok=True)
    else:
        await asyncio.to_thread(os.chdir, base_dir)
        await asyncio.to_thread(os.makedirs, data_directory_name, exist_ok=True)
        await asyncio.to_thread(os.chdir, data_dir)
        await asyncio.to_thread(os.makedirs, name_of_the_directory, exist_ok=True)

async def just_create_folder(folder_name : str,user_name : str):
    path = os.getenv('PATH_TO_THE_DATA_DIRECTORY') + "/" + user_name
    if await asyncio.to_thread(os.path.exists,path):
        await asyncio.to_thread(os.chdir,path)
        await asyncio.to_thread(os.makedirs,folder_name)

