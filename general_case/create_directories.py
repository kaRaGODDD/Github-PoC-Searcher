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
