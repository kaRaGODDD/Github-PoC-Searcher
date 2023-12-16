import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

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

